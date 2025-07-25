import json
import sys
import xapian
from sickle import Sickle
from sickle.oaiexceptions import *
from urllib.parse import urlparse
import logging
from amwmeta.utils import DataPage, strip_diacritics
from sickle.models import Record
import re
from unidecode import unidecode
import pprint

pp = pprint.PrettyPrinter(indent=2)


logger = logging.getLogger(__name__)

# slot, prefix, boolean
FIELD_MAPPING = [
        ( 'title',     1, 'S',   False, 'title'),
        ( 'creator',   2, 'XA',  True,  None),
        ( 'creator',   3, 'A',   False, 'author'),
        ( 'date',      4, 'XP',  True,  None),
        ( 'language',  5, 'L',   True,  None),
        ( 'library',   6, 'XH',  True,  None),
        ( 'aggregate', 11, 'XG', True,  None),
        ( 'download',  12, 'XD', True,  None),
        ( 'translate', 13, 'XT', True,  None),
]
# public prefix is 'P'

SORTABLE_FIELDS = {
    "date": (7, 'number'),
    "title": (8, 'string'),
    "datestamp": (9, 'timestamp'),
    "last_modified": (10, 'timestamp'),
}
SORT_DIRECTIONS = {
    "asc": False,
    "desc": True,
}

# XH is unique source
EXCLUSION_FIELDS = {
    'library': 'XH',
    'creator': 'XA',
    'entry': 'Q',
}

def search(db_path, query_params,
           active_libraries=[],
           exclusions=[],
           facets_only=False,
           partial_match=False,
           matches_only=False):
    db = xapian.Database(db_path)
    querystring = strip_diacritics(query_params.get("query"))

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
        # if boolean
        if field[3]:
            queryparser.add_boolean_prefix(field[0], field[2])
        elif field[4]:
            queryparser.add_prefix(field[4], field[2])

    excluded_libraries = { i[1]: True for i in exclusions if i[0] == 'library' }
    logger.debug("Excluded libraries: {}".format(excluded_libraries))

    context = {}
    spies = {}
    if querystring:
        context['querystring'] = querystring
    query = xapian.Query.MatchAll
    queryparser.set_default_op(xapian.Query.OP_AND)
    if querystring:
        # logger.info("Query is " + querystring)
        flags = queryparser.FLAG_PHRASE | queryparser.FLAG_BOOLEAN  | queryparser.FLAG_LOVEHATE | queryparser.FLAG_WILDCARD
        if partial_match:
            flags = flags | queryparser.FLAG_PARTIAL
        query = queryparser.parse_query(querystring, flags)

    filter_queries = []
    active_facets = {}
    if not matches_only:
        for field in FIELD_MAPPING:
            # booleans only
            if field[3]:
                field_name = field[0]
                filters_ors = []
                active_facets[field_name] = []
                for value in query_params.getlist('filter_' + field_name):
                    if value:
                        filter_value = field[2] + value.lower();
                        logger.debug("Filter value is " + filter_value)
                        filters_ors.append(xapian.Query(filter_value))
                        active_facets[field_name].append(value)
                if len(filters_ors):
                    filter_queries.append(xapian.Query(xapian.Query.OP_OR, filters_ors))

    # logger.info(filter_queries)
    if active_libraries:
        filter_queries.append(xapian.Query(xapian.Query.OP_OR, [ xapian.Query('XH{}'.format(i)) for i in active_libraries ]))
    else:
        # this shouldn't happen
        filter_queries.append(xapian.Query('P1'))

    if len(filter_queries):
        query = xapian.Query(xapian.Query.OP_FILTER, query,
                             xapian.Query(xapian.Query.OP_AND, filter_queries))

    # blacklist
    if exclusions:
        excluded = [ xapian.Query(EXCLUSION_FIELDS[q[0]] + str(q[1])) for q in exclusions ]
        query = xapian.Query(xapian.Query.OP_AND_NOT,
                             query,
                             xapian.Query(xapian.Query.OP_OR, excluded))

    enquire = xapian.Enquire(db)
    logger.debug(query)
    enquire.set_query(query)
    logger.debug(query_params)

    web_sorting = {
        'title_asc': ('title', 'asc'),
        'title_desc': ('title', 'desc'),
        'datestamp': ('datestamp', 'desc'),
    }
    web_sorting_chosen = web_sorting.get(query_params.get('sort_by', 'datestamp'))
    if facets_only:
        pass
    elif web_sorting_chosen:
        sort_by, sort_dir = web_sorting_chosen
        logger.debug("Sorting by {} {}".format(sort_by, sort_dir))
        enquire.set_sort_by_value_then_relevance(SORTABLE_FIELDS.get(sort_by)[0], SORT_DIRECTIONS.get(sort_dir))
    else:
        logger.debug("Default sorting (relevance)")

    matches = []
    facets = {}
    for field in FIELD_MAPPING:
        # boolean only
        if field[3]:
            # use the slot
            spy = xapian.ValueCountMatchSpy(field[1])
            enquire.add_matchspy(spy)
            spies[field[0]] = spy

    start = (page_number - 1) * page_size
    mset = enquire.get_mset(start, page_size, db.get_doccount())
    total_entries = mset.get_matches_estimated()
    pager = DataPage(total_entries=total_entries,
                     entries_per_page=page_size,
                     current_page=page_number)
    if not facets_only:
        for matched in mset:
            fields = json.loads(matched.document.get_data().decode('utf8'))
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
            # if there are excluded sites, also remove them from here.
            # Sole source are already filtered out.
            # TODO There the case where the other one is private and does
            # not show up. In that case it will have no link and no
            # reference. So it's not showing up because it's excluded,
            # while the other is private, so it's not seen as an unique
            # source
            if active_libraries:
                rec['data_sources'] = [ ds for ds in rec['data_sources'] if ds['library_id'] in active_libraries ]
            else:
                rec['data_sources'] = [ ds for ds in rec['data_sources'] if ds['public'] ]
            if exclusions:
                rec['data_sources'] = [ ds for ds in rec['data_sources'] if not excluded_libraries.get(ds['library_id']) ]
            matches.append(rec)

    if matches_only:
        return matches

    for spy_name in spies:
        spy = spies[spy_name]
        facet_values = {}
        for facet in spy.values():
            # logger.debug(facet.term)
            for facet_structure in json.loads(facet.term.decode('utf-8')):
                facet_id = facet_structure['id']

                if facet_id in facet_values:
                    facet_values[facet_id]['count'] += facet.termfreq
                else:
                    facet_values[facet_id] = {
                        "id": facet_structure['id'],
                        "term": str(facet_structure['value']),
                        "count": facet.termfreq,
                        "key": spy_name + str(facet_structure['id']),
                    }

        if len(facet_values):
            facets[spy_name] = {
                "name": spy_name,
                "values": sorted(list(facet_values.values()), key=lambda el: (0 - el['count'], str(el['term']))),
            }

    context['matches'] = matches

    if facets.get('library'):
        facets['library']['values'] = [ v for v in facets['library']['values'] if v['id'] in active_libraries ]

    # if there are excluded libraries, remove them as well
    if exclusions and facets.get('library'):
        facets['library']['values'] = [ v for v in facets['library']['values'] if not excluded_libraries.get(v['id']) ]

    if facets_only:
        return facets

    context['facets'] = facets
    context['filters'] = active_facets
    context['pager'] = pager
    context['querystring'] = querystring

    return context

class MycorrhizaIndexer:
    # kw only argument
    def __init__(self, *, db_path):
        logger.info("Initializing MycorrhizaIndexer with " + db_path)
        self.db = xapian.WritableDatabase(db_path, xapian.DB_CREATE_OR_OPEN)
        self.logs = []

    def index_record(self, record):
        is_deleted = True
        termgenerator = xapian.TermGenerator()
        termgenerator.set_stemmer(xapian.Stem("none"))

        # logger.debug(pp.pformat(record))
        if len(record['data_sources']) > 0 or record['is_aggregation']:
            is_deleted = False

        identifier = record['entry_id']
        doc = xapian.Document()
        termgenerator.set_document(doc)

        doc.add_boolean_term("XH{}".format(record['unique_source']))

        if record['public']:
            doc.add_boolean_term('P1')
        else:
            doc.add_boolean_term('P0')

        for field in FIELD_MAPPING:
            field_name, slot, prefix, is_boolean, search_prefix = field
            values = record.get(field_name)

            if values:
                value_list = []
                for v in values:
                    if v:
                        if is_boolean:
                            # logger.debug("Adding boolean {}".format(prefix + str(v['id'])))
                            doc.add_boolean_term(prefix + str(v['id']))
                        else:
                            termgenerator.index_text(strip_diacritics(str(v['value'])), 1, prefix)
                        value_list.append(v)

                doc.add_value(slot, json.dumps(value_list))

        for field in SORTABLE_FIELDS:
            slot, sort_type = SORTABLE_FIELDS[field]
            sort_value = record.get(field)
            # print("Sort value for {} is {}".format(field, sort_value))
            if sort_value is not None and len(sort_value) > 0:
                # print(sort_value)
                if sort_type == 'number':
                    doc.add_value(slot, xapian.sortable_serialise(sort_value[0]['value']))
                elif sort_type == 'timestamp':
                    # logger.info("Adding {} {} for {}".format(slot, sort_value, identifier))
                    doc.add_value(slot, sort_value)
                elif sort_type == 'string':
                    stripped = unidecode(' '.join([ v['value'] for v in sort_value ])).lower()
                    stripped = re.sub(r'^[^a-z0-9]+', '', stripped)
                    doc.add_value(slot, stripped)

        # general search
        for field in ['title', 'creator']:
            termgenerator.increase_termpos()
            values = record.get(field)
            for v in values:
                # logger.debug("Indexing {} {}".format(field, v['value']))
                termgenerator.index_text(strip_diacritics(v['value']), 20)

        # This can be used to prevent phrase searches from spanning
        # two unconnected blocks of text (e.g. the title and body
        # text).
        termgenerator.increase_termpos()

        # index the original authors and titles as received,
        # regardless of the merging (which is the boolean ones).

        for dsd in record['data_sources']:
            # index the original author as a string
            for value in dsd.get('authors'):
                termgenerator.index_text(strip_diacritics(value), 20)
            for field in [ 'title', 'subtitle' ]:
                value = dsd.get(field)
                if value:
                    termgenerator.index_text(strip_diacritics(value), 20)

        for field in ['description', 'material_description', 'publisher', 'isbn']:
            termgenerator.increase_termpos()
            for dsd in record['data_sources']:
                value = dsd.get(field)
                if value:
                    # logger.debug("Indexing {} {}".format(field, value))
                    termgenerator.index_text(strip_diacritics(value), 10)

        # if aggregation or aggregated, index titles and authors of
        # the related one as well.

        for dsd in record['data_sources']:
            for aggfield in ['aggregations', 'aggregated']:
                for agg in dsd[aggfield]:
                    termgenerator.increase_termpos()
                    for author in agg.get('authors', []):
                        termgenerator.index_text(strip_diacritics(author), 20)
                    for field in ['title', 'description']:
                        value = agg.get(field)
                        if value:
                            termgenerator.index_text(strip_diacritics(value), 20)

        for ft in record.pop('full_texts'):
            if ft:
                logger.debug("Indexing full text with {} chars".format(len(ft)))
                termgenerator.increase_termpos()
                termgenerator.index_text(strip_diacritics(ft))

        doc.set_data(json.dumps(record))
        idterm = "Q{}".format(identifier)
        doc.add_boolean_term(idterm)
        if is_deleted:
            logger.info("Removing document " + idterm)
            self.logs.append("Removing document " + idterm)
            self.db.delete_document(idterm)
        else:
            logger.info("Indexing document " + idterm)
            self.logs.append("Indexing " + idterm)
            self.db.replace_document(idterm, doc)
