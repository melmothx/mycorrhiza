import json
import sys
import xapian
from sickle import Sickle
from sickle.oaiexceptions import *
from urllib.parse import urlparse
from pathlib import Path
import logging
from amwmeta.utils import DataPage
from sickle.models import Record
import re
from unidecode import unidecode

logger = logging.getLogger(__name__)

XAPIAN_DB = str(Path(__file__).resolve().parent.parent.joinpath('xapian', 'db'))

# slot, prefix, boolean
FIELD_MAPPING = {
        'title':    (1, 'S',  False),
        'creator':  (2, 'XA', True),
        'subject':  (3, 'XK', True),
        'date':     (4, 'XP', True),
        'language': (5, 'L',  True),
        'site':     (6, 'H',  True),
}
# public prefix is 'P'

SORTABLE_FIELDS = {
    "date": (7, 'number'),
    "title": (8, 'string'),
}
SORT_DIRECTIONS = {
    "asc": False,
    "desc": True,
}

def search(query_params, public_only=True, active_sites={}):
    db = xapian.Database(XAPIAN_DB)
    querystring = query_params.get("query")

    # todo setup validation in the views.py
    page_size = int(query_params.get("page_size", 10))
    if page_size < 1:
        page_size = 10

    page_number = int(query_params.get("page_number", 1))
    if page_number < 1:
        page_number = 1

    queryparser = xapian.QueryParser()
    queryparser.set_stemmer(xapian.Stem("none"))
    queryparser.set_stemming_strategy(queryparser.STEM_NONE)

    for field in FIELD_MAPPING:
        if FIELD_MAPPING[field][2]:
            queryparser.add_boolean_prefix(field, FIELD_MAPPING[field][1])
        else:
            queryparser.add_prefix(field, FIELD_MAPPING[field][1])

    context = {}
    spies = {}
    if querystring:
        context['querystring'] = querystring
    query = xapian.Query.MatchAll
    queryparser.set_default_op(xapian.Query.OP_AND)
    if querystring:
        logger.info("Query is " + querystring)
        flags = queryparser.FLAG_PHRASE | queryparser.FLAG_BOOLEAN  | queryparser.FLAG_LOVEHATE | queryparser.FLAG_WILDCARD
        query = queryparser.parse_query(querystring, flags)

    filter_queries = []
    active_facets = {}
    for field in FIELD_MAPPING:
        # booleans only
        if FIELD_MAPPING[field][2]:
            filters_ors = []
            active_facets[field] = []
            for value in query_params.getlist('filter_' + field):
                if value:
                    filter_value = FIELD_MAPPING[field][1] + value.lower();
                    logger.info("Filter value is " + filter_value)
                    filters_ors.append(xapian.Query(filter_value))
                    active_facets[field].append(value)
            if len(filters_ors):
                filter_queries.append(xapian.Query(xapian.Query.OP_OR, filters_ors))

    logger.info(filter_queries)
    if public_only:
        filter_queries.append(xapian.Query('P1'))

    if len(filter_queries):
        query = xapian.Query(xapian.Query.OP_FILTER, query,
                             xapian.Query(xapian.Query.OP_AND, filter_queries))

    enquire = xapian.Enquire(db)
    enquire.set_query(query)

    sort_by = SORTABLE_FIELDS.get(query_params.get('sort_by', ''), SORTABLE_FIELDS['title'])[0]
    sort_dir = SORT_DIRECTIONS.get(query_params.get('sort_direction', ''), SORT_DIRECTIONS['asc'])
    # search without sort specified
    if querystring and not query_params.get('sort_by'):
        logger.info("Sorting by relevance")
        enquire.set_sort_by_relevance_then_value(sort_by, sort_dir)
    else:
        logger.info("Sorting by value")
        enquire.set_sort_by_value_then_relevance(sort_by, sort_dir)

    matches = []
    facets = {}
    for field in FIELD_MAPPING:
        # boolean only
        if FIELD_MAPPING[field][2]:
            # use the slot
            spy = xapian.ValueCountMatchSpy(FIELD_MAPPING[field][0])
            enquire.add_matchspy(spy)
            spies[field] = spy

    start = (page_number - 1) * page_size
    mset = enquire.get_mset(start, page_size, db.get_doccount())
    pager = DataPage(total_entries=mset.get_matches_estimated(),
                     entries_per_page=page_size,
                     current_page=page_number)
    logger.info(pager)

    for match in mset:
        fields = json.loads(match.document.get_data().decode('utf8'))
        rec = {}
        for field in fields:
            values = fields.get(field)
            if values:
                if field == "identifier":
                    urls = [ i for i in values if re.match(r'^https?://', i) ]
                    if len(urls):
                        rec['url'] = urls[0]
                        rec['identifiers'] = values
                else:
                    rec[field] = values

        # logger.info(rec)
        if public_only:
            rec['data_sources'] = [ ds for ds in rec['data_sources'] if ds['public'] ]
        matches.append(rec)

    for spy_name in spies:
        spy = spies[spy_name]
        facet_values = {}
        for facet in spy.values():
            # logger.debug(facet.term)
            for facet_structure in json.loads(facet.term.decode('utf-8')):
                facet_value = facet_structure['value']
                facet_active = False
                if facet_value in active_facets[spy_name]:
                    facet_active = True

                if facet_value in facet_values:
                    facet_values[facet_value]['count'] += facet.termfreq
                else:
                    facet_values[facet_value] = {
                        "id": facet_structure['id'],
                        "term": str(facet_value),
                        "count": facet.termfreq,
                        "active": facet_active,
                        "key": spy_name + str(facet_structure['id']),
                    }

        if len(facet_values):
            facets[spy_name] = {
                "name": spy_name,
                "values": sorted(list(facet_values.values()), key=lambda el: (0 - el['count'], str(el['term']))),
            }

    context['matches'] = matches
    if public_only and facets.get('site', False):
        facets['site']['values'] = [ v for v in facets['site']['values'] if active_sites.get(v['id'], False) ]

    context['facets'] = facets
    context['filters'] = active_facets
    context['pager'] = pager
    context['querystring'] = querystring

    return context

class MycorrhizaIndexer:
    def __init__(self):
        self.db = xapian.WritableDatabase(XAPIAN_DB, xapian.DB_CREATE_OR_OPEN)
        self.logs = []

    def index_entries(self, entries):
        for e in entries:
            self.index_record(e.indexing_data())

    def index_record(self, record):
        is_deleted = True
        termgenerator = xapian.TermGenerator()
        termgenerator.set_stemmer(xapian.Stem("none"))

        if len(record['data_sources']) > 0:
            is_deleted = False

        identifier = record['entry_id']
        doc = xapian.Document()
        termgenerator.set_document(doc)

        if record['public']:
            doc.add_boolean_term('P1')
        else:
            doc.add_boolean_term('P0')

        for field in FIELD_MAPPING:
            values = record.get(field)
            slot, prefix, is_boolean = FIELD_MAPPING[field]
            if values:
                value_list = []
                for v in values:
                    if v:
                        if is_boolean:
                            doc.add_boolean_term(prefix + str(v['id']))
                        termgenerator.index_text(str(v['value']), 1, prefix)
                        value_list.append(v)

                doc.add_value(slot, json.dumps(value_list))

        for field in SORTABLE_FIELDS:
            slot, sort_type = SORTABLE_FIELDS[field]
            sort_value = record.get(field)
            if sort_value is not None and len(sort_value) > 0:
                # print(sort_value)
                if sort_type == 'number':
                    doc.add_value(slot, xapian.sortable_serialise(sort_value[0]['value']))
                elif sort_type == 'string':
                    doc.add_value(slot, unidecode(' '.join([ v['value'] for v in sort_value ])).lower())

        # general search
        for field in ['title', 'creator', 'subject', 'description']:
            termgenerator.increase_termpos()
            values = record.get(field)
            for v in values:
                termgenerator.index_text(v['value'])

        doc.set_data(json.dumps(record))
        idterm = "Q{}".format(identifier)
        doc.add_boolean_term(idterm)
        if is_deleted:
            self.logs.append("Removing document " + idterm)
            self.db.delete_document(idterm)
        else:
            self.logs.append("Indexing " + idterm)
            self.db.replace_document(idterm, doc)
