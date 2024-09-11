from django.db import models
from amwmeta.harvest import harvest_oai_pmh, extract_fields
from urllib.parse import urlparse
from datetime import datetime, timezone
from django.db import transaction
from django.contrib.auth.models import AbstractUser
from amwmeta.xapian import MycorrhizaIndexer
from amwmeta.calibre import scan_calibre_tree
from django.conf import settings
import logging
from amwmeta.sheets import parse_sheet
import random
import requests
import re
import pprint
import hashlib
from pathlib import Path

pp = pprint.PrettyPrinter(indent=2)
logger = logging.getLogger(__name__)

def log_user_operation(user, op, canonical, alias):
    if user and op and canonical:
        canonical_title = "canonical"
        alias_title = "alias"
        if "translation" in op:
            canonical_title = "original"
            alias_title = "translation"
        elif "aggregation" in op:
            canonical_title = "aggregation"
            alias_title = "aggregated"
        elif "exclusion" in op:
            canonical_title = "excluded"
            alias_title = "excluded"


        if alias:
            comment = "{}: {} ({})\n{}: {} ({})".format(canonical_title, canonical.display_name(), canonical.id,
                                                        alias_title, alias.display_name(), alias.id)
            alias.changelogs.create(
                user=user,
                username=user.username,
                operation=op,
                comment=comment,
            )
        else:
            comment = "{}: {} ({})".format(canonical_title, canonical.display_name(), canonical.id)

        canonical.changelogs.create(
            user=user,
            username=user.username,
            operation=op,
            comment=comment,
        )

class Library(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255,
                          blank=True,
                          null=True)
    public = models.BooleanField(default=False, null=False)
    active = models.BooleanField(default=True, null=False)
    email_public = models.EmailField(blank=True)
    email_internal = models.EmailField(blank=True)
    opening_hours = models.TextField(blank=True)
    latitude  = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=7)
    longitude = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=7)
    description = models.TextField(blank=True)
    logo_url = models.URLField(max_length=255,
                               blank=True,
                               null=True)
    languages = models.TextField(blank=True)
    year_established = models.DateField(null=True, blank=True)
    enable_check = models.BooleanField(default=False)
    check_token = models.CharField(max_length=255, blank=True)
    last_check = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "{} [{}]".format(self.name, self.id)
    def as_api_dict(self):
        out = {}
        for f in ["id", "name", "url", "public", "active"]:
            out[f] = getattr(self, f)
        out['created'] = self.created.strftime('%Y-%m-%dT%H:%M')
        out['last_modified'] = self.last_modified.strftime('%Y-%m-%dT%H:%M')
        return out

    def public_data(self):
        out = { "established": None }
        public_fields = ["id", "name", "url", "email_public", "opening_hours",
                         "description", "logo_url", "languages",
                         "latitude", "longitude"]
        for f in public_fields:
            out[f] = getattr(self, f)
        if self.year_established:
            out['established'] = self.year_established.strftime('%Y')
        return out

    class Meta:
        verbose_name_plural = "Libraries"

class User(AbstractUser):
    email = models.EmailField(null=False, blank=False)
    libraries = models.ManyToManyField(Library, related_name="affiliated_users")
    library_admin = models.BooleanField(default=False)
    can_merge = models.BooleanField(default=False)
    expiration = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_expiration = models.DateTimeField(null=True, blank=True)

    def has_valid_password_reset(self):
        if self.password_reset_token and self.password_reset_expiration > datetime.now(timezone.utc):
            return True
        else:
            return False

    def can_merge_entries(self):
        if self.library_admin:
            return True
        elif self.can_merge:
            return True
        else:
            return False



class Site(models.Model):
    OAI_DC = "oai_dc"
    MARC21 = "marc21"
    OAI_PMH_METADATA_FORMATS = [
        (OAI_DC, "Dublin Core"),
        (MARC21, "MARC XML"),
    ]
    CSV_TYPES = [
        ('calibre', 'Calibre'),
        ('abebooks_home_base', 'Abebooks Home Base'),
        ('disordine', 'Biblioteca Disordine'),
    ]
    SITE_TYPES = [
        ('amusewiki', "Amusewiki"),
        ('generic', "Generic OAI-PMH"),
        ('csv', "CSV Upload"),
        ('calibretree', "Calibre File Tree"),
    ]
    library = models.ForeignKey(Library,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name="sites")
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, max_length=255)
    last_harvested = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    oai_set = models.CharField(max_length=64,
                               blank=True,
                               null=True)
    oai_metadata_format = models.CharField(max_length=32,
                                           null=True,
                                           blank=True,
                                           choices=OAI_PMH_METADATA_FORMATS)
    site_type = models.CharField(max_length=32, choices=SITE_TYPES, default="generic")
    csv_type = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        choices=CSV_TYPES,
    )
    active = models.BooleanField(default=True, null=False)
    amusewiki_formats = models.JSONField(null=True)
    tree_path = models.CharField(blank=True, null=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({} - {})".format(self.title, self.library.name, self.site_type)

    def last_harvested_zulu(self):
        dt = self.last_harvested
        if dt:
            # clone
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return None

    def hostname(self):
        url = self.url
        if not url:
            url = self.library.url
        if url:
            return urlparse(url).hostname
        else:
            return "unknown-{}".format(self.id)

    def record_aliases(self):
        aliases = {
            "author": {},
            "language": {},
            "title": {},
            "subtitle": {},
        }
        for al in self.namealias_set.all():
            aliases[al.field_name][al.value_name] = al.value_canonical
        return aliases

    def update_amusewiki_formats(self):
        if self.site_type == 'amusewiki':
            base_uri = urlparse(self.url)
            endpoint = "{0}://{1}/api/format-definitions".format(base_uri.scheme,
                                                                 base_uri.hostname)
            r = requests.get(endpoint)
            if r.status_code == 200:
                self.amusewiki_formats = r.json()
                # for amusewikis, enforce the web set
                self.oai_set = 'web'
                self.save()
            else:
                logger.debug("GET {0} returned {1}".format(r.url, r.status_code))
        else:
            self.amusewiki_formats = None
            self.save()

    def harvest(self, force=False):
        if self.site_type in ['amusewiki', 'generic']:
            self.pmh_harvest(force=force)
        elif self.site_type == 'calibretree':
            self.process_calibre_tree()
        else:
            pass

    def pmh_harvest(self, force=False):
        self.update_amusewiki_formats()
        url = self.url
        hostname = self.hostname()
        now = datetime.now(timezone.utc)
        opts = {
            "metadataPrefix": self.oai_metadata_format,
        }
        last_harvested = self.last_harvested_zulu()
        logger.debug([ force, last_harvested ])
        set_last_harvested = True
        if last_harvested and not force:
            opts['from'] = last_harvested
        elif self.oai_set:
            opts['set'] = self.oai_set

        xapian_records = []
        if force:
            # before deleting, store the entry ids so we can reindex
            # them. Entries without associated datasources will be
            # removed from the index.
            xapian_records = [ i.entry_id for i in self.datasource_set.all() ]
            self.datasource_set.all().delete()

        records = harvest_oai_pmh(url, opts)

        aliases = self.record_aliases()
        counter = 0
        for rec in records:
            counter += 1
            if counter % 10 == 0:
                logger.debug(str(counter) + " records done")
            full_data = rec.get_metadata()
            record = extract_fields(full_data, hostname)
            record['deleted'] = rec.deleted
            record['identifier'] = rec.header.identifier
            record['full_data'] = full_data
            try:
                record['datestamp'] = datetime.fromisoformat(rec.header.datestamp)
            except ValueError:
                record['datestamp'] = now

            for entry in self.process_harvested_record(record, aliases, now):
                if entry is None:
                    logger.info("Skipping {} deleted? {}, returned None".format(rec.header.identifier, rec.deleted))
                else:
                    xapian_records.append(entry.id)
        # and index
        self.index_harvested_records(xapian_records, force=force, now=now, set_last_harvested=set_last_harvested)

    def index_harvested_records(self, xapian_records, force=False, now=None, set_last_harvested=True):
        indexer = MycorrhizaIndexer(db_path=settings.XAPIAN_DB)
        all_ids = list(set(xapian_records))
        logger.debug("Indexing " + str(all_ids))
        for iid in all_ids:
            try:
                ientry = Entry.objects.get(pk=iid)
                indexer.index_record(ientry.indexing_data())
            except Entry.DoesNotExist:
                logger.info("Entry id {} not found?!".format(iid))

        logs = indexer.logs
        if logs:
            msg = "Total indexed: " + str(len(logs))
            # logger.info(msg)
            logs.append(msg)
            if set_last_harvested:
                logger.info("Setting last harvested to {}".format(now))
                self.last_harvested = now
                self.save()
            self.harvest_set.create(datetime=now, logs="\n".join(logs))

    def process_harvested_record(self, record, aliases, now):
        aggregations = record.pop('aggregations', [])
        entry, ds = self._process_single_harvested_record(record, aliases, now, is_aggregation=False)
        out = []
        if entry and ds:
            out.append(entry)
            for agg in aggregations:
                agg_record = {
                    "title": agg['full_aggregation_name'],
                    "full_data": agg,
                    "identifier": agg['identifier'],
                    "uri": agg.get('linkage'),
                    "uri_label": ds.uri_label,
                    "year_edition": ds.year_edition,
                    "year_first_edition": ds.year_first_edition,
                    "content_type": ds.content_type,
                    "deleted": False,
                    "checksum": agg['checksum'],
                    "datestamp": ds.datestamp,
                }
                agg_entry, agg_ds = self._process_single_harvested_record(agg_record, aliases, now, is_aggregation=True)
                out.append(agg_entry)
                entry_rel = {
                    "aggregation": agg_entry,
                    "aggregated": entry,
                }
                ds_rel_spec = {
                    "aggregation": agg_ds,
                    "aggregated": ds,
                }
                try:
                    AggregationEntry.objects.get(**entry_rel)
                except AggregationEntry.DoesNotExist:
                    AggregationEntry.objects.create(**entry_rel)

                try:
                    relation = AggregationDataSource.objects.get(**ds_rel_spec)
                except AggregationDataSource.DoesNotExist:
                    relation = AggregationDataSource.objects.create(**ds_rel_spec)

                if agg.get('order'):
                    try:
                        relation.sorting_pos = agg.get('order')
                        relation.save()
                    except ValueError:
                        relation.sorting_pos = None
                        relation.save()
        return out

    def _process_single_harvested_record(self, record, aliases, now, is_aggregation=False):

        authors = []
        languages = []
        for author in record.pop('authors', []):
            author_name = author
            if aliases and aliases.get('author'):
                author_name=aliases['author'].get(author, author)
            obj, was_created = Agent.objects.get_or_create(name=author_name)
            authors.append(obj)

        for language in record.pop('languages', []):
            lang = language[0:3]
            if aliases and aliases.get('language'):
                lang = aliases['language'].get(lang, lang)
            obj, was_created = Language.objects.get_or_create(code=lang)
            languages.append(obj)


        logger.debug(record)
        identifier = record.pop('identifier')

        ds_attributes = [
            'full_data',
            'uri',
            'uri_label',
            'content_type',
            'shelf_location_code',
            'material_description',
            'year_edition',
            'year_first_edition',
            'description',
            'isbn',
            'publisher',
        ]
        ds_attrs = { x: record.pop(x, None) for x in ds_attributes }

        ds_identifiers = {
            "oai_pmh_identifier": identifier,
            "is_aggregation": is_aggregation,
        }
        try:
            ds = self.datasource_set.get(**ds_identifiers)
            for attr, value in ds_attrs.items():
                setattr(ds, attr, value)
            ds.save()
        except DataSource.DoesNotExist:
            ds = self.datasource_set.create(**ds_identifiers, **ds_attrs)

        # if not provided, use the current time if the datestamp is null
        if record.get('datestamp'):
            ds.datestamp = record.pop('datestamp')
            ds.save()
        elif not ds.datestamp:
            ds.datestamp = now
            ds.save()

        for f in [ 'title', 'subtitle' ]:
            f_value = record.get(f, '')
            if f_value and len(f_value) > 250:
                f_value = f_value[0:250] + '...'
            if aliases and aliases.get(f):
                f_value = aliases[f].get(f_value, f_value)
            record[f] = f_value

        # if the OAI-PMH record has already a entry attached from a
        # previous run, that's it, just update it.
        entry = ds.entry
        if record.pop('deleted'):
            ds.delete()
            return (entry, None)

        if not record.get('checksum'):
            raise Exception("Expecting checksum in normal entry")

        if not entry:
            # check if there's already a entry with the same checksum.
            try:
                entry = Entry.objects.get(checksum=record['checksum'], is_aggregation=is_aggregation)
            except Entry.DoesNotExist:
                entry = Entry.objects.create(**record, is_aggregation=is_aggregation)
            except Entry.MultipleObjectsReturned:
                entry = Entry.objects.filter(checksum=record['checksum'], is_aggregation=is_aggregation).first()
            ds.entry = entry
            ds.save()

        # update the entry and assign the many to many
        for attr, value in record.items():
            setattr(entry, attr, value)

        entry.authors.set(authors)
        entry.languages.set(languages)

        # datestamp: use the most recent
        if not entry.datestamp or ds.datestamp > entry.datestamp:
            entry.datestamp = ds.datestamp

        entry.save()
        return (entry, ds)

    def process_generic_records(self, records, replace_all=False):
        now = datetime.now(timezone.utc)
        hostname = self.hostname()
        aliases = self.record_aliases()
        xapian_records = []
        if replace_all:
            # we need to reindex all the entries
            xapian_records = [ i.entry_id for i in self.datasource_set.all() ]
            self.datasource_set.all().delete()

        logger.debug("Reindexing: {}".format(xapian_records))
        site_type_ids = {
            "calibretree": "ct",
            "csv": "csv",
            "generic": "pmh",
            "amusewiki": "amw",
        }
        for full in records:
            # logger.debug(full)
            record = extract_fields(full, hostname)
            if full.get('identifier'):
                record['identifier'] = '{}:{}:{}'.format(site_type_ids.get(self.site_type, "x"),
                                                         hostname,
                                                         full['identifier'][0])
            record['full_data'] = full
            record['deleted'] = False
            for entry in self.process_harvested_record(record, aliases, now):
                xapian_records.append(entry.id)
        self.index_harvested_records(xapian_records, force=replace_all, now=now)

    def process_calibre_tree(self):
        if self.site_type == 'calibretree' and self.tree_path:
            records = scan_calibre_tree(self.tree_path)
            logger.debug(pp.pprint(records))
            self.process_generic_records(records)

# these are a level up from the oai pmh records

class Agent(models.Model):
    name = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    description = models.TextField()
    canonical_agent = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name="variant_agents",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def display_name(self):
        return self.name

    def as_api_dict(self, get_canonical=False):
        out = {}
        for f in ["id", "name", "first_name", "last_name", "description", "canonical_agent_id"]:
            out[f] = getattr(self, f)

        out['created'] = self.created.strftime('%Y-%m-%dT%H:%M')
        out['last_modified'] = self.last_modified.strftime('%Y-%m-%dT%H:%M')
        canonical = self.canonical_agent
        if canonical:
            if get_canonical:
                out['canonical'] = canonical.as_api_dict(get_canonical=False)
            else:
                out['canonical'] = canonical.name
        else:
            out['canonical'] = None
        return out

    @classmethod
    def merge_records(cls, canonical, aliases, user=None):
        canonical.canonical_agent = None
        canonical.save()
        reindex_agents = aliases[:]
        reindex_agents.append(canonical)
        for aliased in aliases:
            aliased.canonical_agent = canonical
            aliased.save()
            log_user_operation(user, 'add-merge-agent', canonical, aliased)
            for va in aliased.variant_agents.all():
                va.canonical_agent = canonical
                va.save()
                log_user_operation(user, 'add-merge-agent', canonical, va)
                reindex_agents.append(va)
        entries = []
        for agent in reindex_agents:
            for entry in agent.authored_entries.all():
                entries.append(entry)
        return entries

    def unmerge(self, user=None):
        entries = [ entry for entry in self.authored_entries.all() ]
        if self.canonical_agent:
            canonical = self.canonical_agent
            self.canonical_agent = None
            self.save()
            log_user_operation(user, 'remove-merge-agent', canonical, self)
            for entry in canonical.authored_entries.all():
                entries.append(entry)
        return entries

    def __str__(self):
        return self.name

class Language(models.Model):
    code = models.CharField(max_length=4, unique=True, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

class Entry(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, null=True)
    authors = models.ManyToManyField(Agent, related_name="authored_entries")
    languages = models.ManyToManyField(Language)
    checksum = models.CharField(max_length=255)
    is_aggregation = models.BooleanField(default=False)
    canonical_entry = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name="variant_entries",
    )
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    indexed_data = models.JSONField(null=True)

    original_entry = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name="translations",
    )
    datestamp = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = "Entries"

    def __str__(self):
        return self.title

    def as_api_dict(self, get_canonical=False, get_original=False):
        out = {}
        for f in ["id", "title", "subtitle", "is_aggregation"]:
            out[f] = getattr(self, f)
        out['authors'] = [ agent.name for agent in self.authors.all() ]
        out['languages'] = [ lang.code for lang in self.languages.all() ]
        out['created'] = self.created.strftime('%Y-%m-%dT%H:%M')
        out['last_modified'] = self.last_modified.strftime('%Y-%m-%dT%H:%M')
        canonical = self.canonical_entry
        if canonical:
            if get_canonical:
                out['canonical'] = canonical.as_api_dict(get_canonical=False)
            else:
                out['canonical'] = canonical.id
        else:
            out['canonical'] = None

        original = self.original_entry
        if original:
            if get_original:
                out['original'] = original.as_api_dict(get_original=False)
            else:
                out['original'] = original.id
        else:
            out['original'] = None

        return out

    def display_name(self):
        return self.title

    def display_dict(self, library_ids):
        out = {}
        indexed = self.indexed_data
        for f in [ 'id', 'title', 'subtitle' ]:
            out[f] = getattr(self, f)
        out['authors'] = indexed.get('creator')
        out['languages'] = indexed.get('language')
        data_sources = []
        for ds in indexed.get('data_sources'):
            # only the sites explicitely set in the argument
            if ds['library_id'] in library_ids:
                data_sources.append(ds)
        out['data_sources'] = sorted(data_sources, key=lambda i: i.get('year_edition') or 0, reverse=True)
        return out

    def display_data(self, library_ids=[]):
        record = self.display_dict(library_ids)
        original = self.original_entry
        if original:
            original_data = original.display_dict(library_ids)

            # if we can't see the entry because there is no data
            # source for that, it does not exist
            if original_data.get('data_sources'):
                record['original_entry'] = original_data
        else:
            original = self

        record['translations'] = []
        # and then the translations
        for tr in original.translations.all():
            if tr.id != self.id:
                tr_data = tr.display_dict(library_ids)
                # ditto. No DS, it does not exist
                if tr_data.get('data_sources'):
                    record['translations'].append(tr_data)

        record['aggregated'] = []
        for agg in original.aggregated_entries.all():
            agg_data = agg.aggregated.display_dict(library_ids)
            if agg_data.get('data_sources'):
                record['aggregated'].append(agg_data)

        record['aggregations'] = []
        for agg in original.aggregation_entries.all():
            agg_data = agg.aggregation.display_dict(library_ids)
            if agg_data.get('data_sources'):
                record['aggregations'].append(agg_data)

        return record

    def indexing_data(self):
        # we index the entries
        data_source_records = []

        # if canonical entry is set, it was merged so it will not be
        # indexed as such.

        if not self.canonical_entry:
            data_source_records = [ xopr for xopr in self.datasource_set.all() ]
            for variant in self.variant_entries.all():
                data_source_records.extend([ xopr for xopr in variant.datasource_set.all() ])

        authors  = []
        for author in self.authors.all():
            real_author = author
            if author.canonical_agent:
                real_author = author.canonical_agent
            authors.append({
                "id": real_author.id,
                "value": real_author.name,
            });

        xapian_data_sources = []
        record_is_public = False
        entry_file_formats = []

        full_texts = []

        for topr in data_source_records:
            dsd = topr.indexing_data()
            # at DS level
            dsd['aggregations'] = [ ds.aggregation.indexing_data() for ds in topr.aggregation_data_sources.order_by('sorting_pos').all() ]
            dsd['aggregated']   = [ ds.aggregated.indexing_data() for ds in topr.aggregated_data_sources.order_by('sorting_pos').all() ]
            xapian_data_sources.append(dsd)
            if dsd['public']:
                record_is_public = True
            for ff in dsd['file_formats']:
                if ff not in entry_file_formats:
                    entry_file_formats.append(ff)

            # this will call the remote
            full_texts.append(topr.full_text())

        entry_libraries = {}
        descriptions = []
        dates = {}
        for topr in data_source_records:
            if not entry_libraries.get(topr.site.library_id):
                entry_library = topr.site.library
                entry_libraries[entry_library.id] = {
                    "id": entry_library.id,
                    "value": entry_library.name,
                }
            if topr.description:
                descriptions.append({
                    "id": "d" + str(topr.id),
                    "value": topr.description,
                })
            if topr.year_first_edition:
                dates[topr.year_first_edition] = True
            if topr.year_edition:
                dates[topr.year_edition] = True

        ff_map = {
            "none": "Bibliographical entry only",
            "raw": "Raw scan",
            "text": "Editable and printable text",
        }
        if not entry_file_formats:
            entry_file_formats.append('none')

        xapian_record = {
            # these are the mapped ones
            "title": [
                { "id": self.id, "value": self.title },
                { "id": self.id, "value": self.subtitle if self.subtitle is not None else "" }
            ],
            "creator": authors,
            "date":     [ { "id": d, "value": d } for d in sorted(list(set(dates))) ],
            "language": [ { "id": l.code, "value": l.code } for l in self.languages.all() ],
            "library": list(entry_libraries.values()),
            "description": descriptions,
            "data_sources": xapian_data_sources,
            "entry_id": self.id,
            "public": record_is_public,
            "last_modified": self.last_modified.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "unique_source": 0,
            "aggregations": [ { "id": agg.aggregation.id, "value": agg.aggregation.title } for agg in self.aggregation_entries.all() ],
            "aggregated": [ { "id": agg.aggregated.id, "value": agg.aggregated.title } for agg in self.aggregated_entries.all() ],
            "is_aggregation": self.is_aggregation,
            "aggregate": [],
            "translate": [],
            "download": [ { "id": eff, "value": ff_map[eff] } for eff in entry_file_formats ],
        }
        if self.datestamp:
            xapian_record["datestamp"] = self.datestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            xapian_record["datestamp"] = self.created.strftime('%Y-%m-%dT%H:%M:%SZ')

        if self.aggregated_entries.count():
            # if it has aggregated entries, it's an aggregation
            xapian_record['aggregate'].append({ "id": "aggregation", "value": "Aggregation" })
        if self.aggregation_entries.count():
            # if it has aggregation entries, it's an aggregated
            xapian_record['aggregate'].append({ "id": "aggregated", "value": "Aggregated" })

        if self.original_entry_id:
            xapian_record['translate'].append({ "id": "translation", "value": "Translations" })
        if self.translations.count():
            xapian_record['translate'].append({ "id": "translated", "value": "Translated Entries" })
        if not xapian_record['translate']:
            xapian_record['translate'].append({ "id": "unknown", "value": "Unknown" })

        # logger.debug(xapian_record)
        if len(xapian_record['library']) == 1:
            xapian_record['unique_source'] = xapian_record['library'][0]['id']

        self.indexed_data = xapian_record
        self.save()

        xapian_record['full_texts'] = full_texts

        return xapian_record

    @classmethod
    def merge_records(cls, canonical, aliases, user=None):
        canonical.canonical_entry = None
        canonical.save()
        reindex = aliases[:]
        for aliased in aliases:
            aliased.canonical_entry = canonical
            aliased.save()
            log_user_operation(user, 'add-merge-entry', canonical, aliased)
            # update the current variant entries
            for ve in aliased.variant_entries.all():
                ve.canonical_entry = canonical
                ve.save()
                log_user_operation(user, 'add-merge-entry', canonical, ve)
                reindex.append(ve)
        # logger.debug(reindex)
        # update the translations
        cls.objects.filter(original_entry__in=reindex).update(original_entry=canonical)
        reindex.append(canonical)
        return reindex

    def unmerge(self, user=None):
        reindex = []
        canonical_entry = self.canonical_entry
        if canonical_entry:
            reindex = [ canonical_entry, self ]
            self.canonical_entry = None
            self.save()
            log_user_operation(user, 'remove-merge-entry', canonical_entry, self)
        return reindex

    @classmethod
    def create_virtual_aggregation(cls, name):
        if name:
            sha = hashlib.sha256()
            sha.update(name.encode())
            record = {
                "title": name,
                "checksum": sha.hexdigest(),
                "is_aggregation": True,
            }
            # here there's no uniqueness in the schema, but we enforce it
            try:
                created = cls.objects.get(**record)
            except cls.DoesNotExist:
                created = cls.objects.create(**record)
            except cls.MultipleObjectsReturned:
                logger.debug("Multiple rows found, using the first")
                created = cls.objects.filter(**record).first()
            return created
        return None

    @classmethod
    def aggregate_entries(cls, aggregation, aggregated_objects, user=None):
        if not aggregation.is_aggregation:
            return []
        reindex = [ aggregation ]
        aggregated_datasources = []
        for aggregated in aggregated_objects:
            reindex.append(aggregated)
            aggregated_datasources.extend([ ds for ds in aggregated.datasource_set.all() ])
            entry_rel = {
                "aggregation": aggregation,
                "aggregated": aggregated,
            }
            try:
                rel = AggregationEntry.objects.get(**entry_rel)
            except AggregationEntry.DoesNotExist:
                rel = AggregationEntry.objects.create(**entry_rel)
                logger.info("Created AggregationEntry {}".format(rel.id))

            log_user_operation(user, 'add-aggregation', aggregation, aggregated)

            # now we have all the aggregated datasources.
            # check if we have a real or virtual DS in the aggregation
            for ds in aggregated_datasources:
                # search all the DS for this aggregation entry with a matching site
                agg_datasources = [ x for x in aggregation.datasource_set.filter(site_id=ds.site_id).all() ]
                if agg_datasources:
                    logger.debug("{} already has an aggregation datasource".format(ds.oai_pmh_identifier))
                else:
                    logger.info("Creating virtual DS for {}".format(ds.oai_pmh_identifier))
                    agg_ds = DataSource.objects.create(
                        site_id=ds.site_id,
                        oai_pmh_identifier="virtual:site-{}:aggregation-{}".format(ds.site_id, aggregation.id),
                        datestamp=aggregation.datestamp,
                        entry_id=aggregation.id,
                        is_aggregation=True,
                        full_data={},
                    )
                    agg_datasources.append(agg_ds)

                for agg_ds in agg_datasources:
                    agg_rel = {
                        "aggregation": agg_ds,
                        "aggregated": ds,
                    }
                    try:
                        rel = AggregationDataSource.objects.get(**agg_rel)
                    except AggregationDataSource.DoesNotExist:
                        rel = AggregationDataSource.objects.create(**agg_rel)
                        logger.info("Created AggregationDataSource {}".format(rel.id))
        return reindex

    @classmethod
    def translate_records(cls, original, translations, user=None):
        reindex = [ original ]
        for translation in translations:
            translation.original_entry = original;
            translation.save()
            log_user_operation(user, 'add-translation', original, translation)
            reindex.append(translation)
        return reindex

    def untranslate(self, user=None):
        reindex = []
        original_entry = self.original_entry
        if original_entry:
            reindex = [ original_entry, self ]
            self.original_entry = None
            self.save()
            log_user_operation(user, 'remove-translation', original_entry, self)
        return reindex




# the OAI-PMH records will keep the URL of the record, so a entry can
# have multiple ones because it's coming from more sources.

# DataSource
class DataSource(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    oai_pmh_identifier = models.CharField(max_length=2048)
    datestamp = models.DateTimeField(null=True)
    full_data = models.JSONField()

    entry = models.ForeignKey(Entry, null=True, on_delete=models.SET_NULL)

    description = models.TextField(null=True)
    year_edition = models.IntegerField(null=True)
    year_first_edition = models.IntegerField(null=True)

    # allow multiple separated by a space
    publisher = models.TextField(null=True)
    isbn = models.TextField(null=True)

    # if digital, provide the url
    uri = models.URLField(max_length=2048, null=True)
    uri_label = models.CharField(max_length=2048, null=True)
    content_type = models.CharField(max_length=128, null=True)
    # if this is the real book, if it exists: phisical description and call number
    material_description = models.TextField(null=True)
    shelf_location_code = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_aggregation = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['site', 'oai_pmh_identifier'], name='unique_site_oai_pmh_identifier'),
        ]
    def __str__(self):
        return self.oai_pmh_identifier

    def amusewiki_base_url(self):
        if self.uri:
            return re.sub(r'((\.[a-z0-9]+)+)$',
                          '',
                          self.uri)
        return None

    def calibre_base_dir(self):
        if self.uri:
            tree = Path(self.uri)
            try:
                if tree.is_dir():
                    return tree
            except PermissionError:
                return None
        return None

    def get_remote_file(self, ext):
        amusewiki_url = self.amusewiki_base_url()
        if amusewiki_url:
            logger.debug("AMW url is " + amusewiki_url)
            return requests.get(amusewiki_url + ext)
        else:
            return None

    def get_calibre_file(self, ext):
        tree = self.calibre_base_dir()
        if tree:
            for f in tree.iterdir():
                if f.suffix == ext:
                    return f
        return None

    def full_text(self):
        site_type = self.site.site_type
        if site_type == 'amusewiki':
            amusewiki_url = self.amusewiki_base_url()
            if amusewiki_url:
                try:
                    r = requests.get(amusewiki_url + '.bare.html')
                    if r.status_code == 200:
                        r.encoding = 'UTF-8'
                        return r.text
                except ConnectionError:
                    logger.info("GET {0} had a connection error".format(endpoint))
                except Timeout:
                    logger.info("GET {0} timed out".format(endpoint))
                except TooManyRedirects:
                    logger.info("GET {0} had too many redirections".format(endpoint))

        elif site_type == 'calibretree':
            tree = self.calibre_base_dir()
            if tree:
                for f in tree.iterdir():
                    if f.suffix == '.txt':
                        text = f.read_text(encoding='UTF-8')
                        replacements = (
                            ('&', '&amp;'),
                            ('<', '&lt;'),
                            ('>', '&gt;'),
                            ('"', '&quot;'),
                            ("'", '&#39;'),
                            ("\n", '<br>'),
                        )
                        for replace in replacements:
                            text = text.replace(replace[0], replace[1],)
                        return text
        return None

    def download_options(self):
        site = self.site
        if self.is_aggregation:
            return []
        elif site.site_type == 'amusewiki':
            # all files are supposed to have the same downloads, more or less
            return site.amusewiki_formats
        elif site.site_type == 'calibretree':
            # the URI here holds the directory, so look into the dir
            downloads = []
            tree = self.calibre_base_dir()
            if tree:
                # we consider just a file per extension. If there are
                # multiple, at this moment we don't care
                download_options = {
                    ".pdf": "PDF",
                    ".epub": "EPUB",
                    ".txt": "TXT",
                }
                seen = []
                for f in tree.iterdir():
                    if f.suffix in download_options:
                        if f.suffix not in seen:
                            downloads.append({
                                "ext": f.suffix,
                                "desc": download_options[f.suffix],
                            })
                            seen.append(f.suffix)
            return downloads
        else:
            return []

    def indexing_data(self):
        site = self.site
        library = site.library
        original_entry = self.entry
        ds = {
            "data_source_id": self.id,
            "identifier": self.oai_pmh_identifier,
            "title": original_entry.title,
            "subtitle": original_entry.subtitle,
            "authors": [ author.name for author in original_entry.authors.all() ],
            "languages": [ lang.code for lang in original_entry.languages.all() ],
            "uri": self.uri,
            # I think these should go
            "uri_label": self.uri_label,
            "content_type": self.content_type,

            "shelf_location_code": self.shelf_location_code,
            "public": False,
            "site_name": site.title,
            "site_id": site.id,
            "site_type": site.site_type,
            "library_id" : library.id,
            "library_name": library.name,
            "description": self.description,
            "year_edition": self.year_edition,
            "year_first_edition": self.year_first_edition,
            "material_description": self.material_description,
            "isbn": self.isbn,
            "publisher": self.publisher,
            "downloads": self.download_options(),
            "entry_id": original_entry.id,
            "file_formats": [],
        }
        if self.datestamp:
            ds["datestamp"] = self.datestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            # probably old records
            ds["datestamp"] = self.created.strftime('%Y-%m-%dT%H:%M:%SZ')

        file_formats = [ ff['ext'] for ff in ds['downloads'] ]

        if '.txt' in file_formats:
            ds['file_formats'].append('text')
        elif '.muse' in file_formats:
            ds['file_formats'].append('text')
        elif '.pdf' in file_formats:
            ds['file_formats'].append('raw')

        if library.active and library.public:
            ds['public'] = True
        return ds

# linking table between entries for aggregations

class AggregationEntry(models.Model):
    aggregation = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="aggregated_entries")
    aggregated  = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="aggregation_entries")
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aggregation', 'aggregated'],
                name='unique_entry_aggregation_aggregated'
            ),
        ]
        verbose_name_plural = "Aggregation Entries"

# linking table between datasource for aggregations

class AggregationDataSource(models.Model):
    aggregation = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name="aggregated_data_sources")
    aggregated  = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name="aggregation_data_sources")
    sorting_pos = models.IntegerField(null=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['aggregation', 'aggregated'],
                name='unique_data_source_aggregation_aggregated'
            ),
        ]

class NameAlias(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    field_name = models.CharField(
        max_length=32,
        choices=[
            ('author', 'Author'),
            ('title', 'Title'),
            ('subtitle', 'Subtitle'),
            ('language', 'Language')
        ]
    )
    value_name = models.CharField(max_length=255, blank=False)
    value_canonical = models.CharField(max_length=255, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['site', 'field_name', 'value_name'],
                name='unique_site_field_name_value_name'
            ),
        ]
        verbose_name_plural = "Name Aliases"

    def __str__(self):
        return self.value_name + ' => ' + self.value_canonical

# this is just to trace the harvesting
class Harvest(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    logs = models.TextField()
    def __str__(self):
        return self.site.title + ' Harvest ' + self.datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

class Exclusion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exclusions")
    exclude_library = models.ForeignKey(Library, null=True, on_delete=models.SET_NULL)
    exclude_author = models.ForeignKey(Agent, null=True, on_delete=models.SET_NULL)
    exclude_entry  = models.ForeignKey(Entry, null=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def display_name(self):
        return "{} {}".format(self.exclusion_type(), self.exclusion_target())

    def exclusion_type(self):
        if self.exclude_library:
            return 'library'
        elif self.exclude_author:
            return 'author'
        elif self.exclude_entry:
            return 'entry'
        else:
            return None

    def exclusion_target(self):
        if self.exclude_library:
            return self.exclude_library.name
        elif self.exclude_author:
            return self.exclude_author.name
        elif self.exclude_entry:
            title = self.exclude_entry.title
            authors = '; '.join([ author.name for author in self.exclude_entry.authors.all() ])
            if authors:
                return "{} ({})".format(title, authors)
            else:
                return title
        else:
            return None

    def as_api_dict(self):
        user = self.user
        out = {
            "id": self.id,
            "excluded_by": {
                "username": user.username,
                "email": user.email,
            },
            "library": self.exclude_library.as_api_dict() if self.exclude_library_id else None,
            "author": self.exclude_author.as_api_dict() if self.exclude_author_id else None,
            "entry": self.exclude_entry.as_api_dict() if self.exclude_entry_id else None,
            "comment": self.comment,
            "created": self.created.strftime('%Y-%m-%dT%H:%M'),
            "last_modified": self.last_modified.strftime('%Y-%m-%dT%H:%M'),
            "type": self.exclusion_type(),
            "target": self.exclusion_target(),
        }
        return out

    def as_xapian_queries(self):
        queries = []
        if self.exclude_library:
            queries.append(('library', self.exclude_library_id))
        if self.exclude_author:
            queries.append(('creator', self.exclude_author_id))
        if self.exclude_entry:
            queries.append(('entry', self.exclude_entry_id))
        return queries

def spreadsheet_upload_directory(instance, filename):
    choices = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ext = '.csv'
    for tryext in ('.xls', '.xlsx'):
        if filename.lower().endswith(tryext):
            ext = tryext
            break

    return "spreadsheets/{0}-{1}.{2}".format(int(datetime.now().timestamp()),
                                             "".join(random.choice(choices) for i in range(20)),
                                             ext)

class SpreadsheetUpload(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="uploaded_spreadsheets",
    )
    spreadsheet = models.FileField(upload_to=spreadsheet_upload_directory)
    comment = models.TextField(blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    replace_all = models.BooleanField(default=False, null=False)
    processed = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    def validate_csv(self):
        return parse_sheet(self.site.csv_type, self.spreadsheet.path, sample=True)

    def process_csv(self):
        now = datetime.now(timezone.utc)
        records = parse_sheet(self.site.csv_type, self.spreadsheet.path)
        self.site.process_generic_records(records, replace_all=self.replace_all)
        self.processed = now
        self.save()


class ChangeLog(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name="changelogs",
    )
    # not a FK, so in case the user is removed, we still have a clue
    username = models.CharField(max_length=255)
    # optionals
    entry     = models.ForeignKey(Entry,     null=True, on_delete=models.SET_NULL, related_name="changelogs")
    agent     = models.ForeignKey(Agent,     null=True, on_delete=models.SET_NULL, related_name="changelogs")
    exclusion = models.ForeignKey(Exclusion, null=True, on_delete=models.SET_NULL, related_name="changelogs")
    operation = models.CharField(max_length=64)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    # last_modified = models.DateTimeField(auto_now=True)

# main router for user operations which need logging.
def manipulate(op, user, main_id, *ids, create=None):
    out = {
        "op": op,
        "main_id": main_id,
        "other_ids": ids,
        "error": None,
        "msg": None,
    }
    if not user:
        out['error']: "Missing User"
        return out

    out['username'] = user.username

    if op == "revert-exclusions" or op == "add-exclusion":
        # we just need the login
        pass
    elif user.is_superuser:
        pass
    elif user.can_merge_entries():
        # needs the can_merge_entries logic
        pass
    else:
        out['error'] = "Cannot do that"
        return out

    logger.info("Calling manipulate " + pp.pformat(out))
    reindex = []
    classes = {
        'merge-agents': Agent,
        'revert-merged-agents': Agent,

        'add-translations': Entry,
        'revert-translations': Entry,

        'merge-entries': Entry,
        'revert-merged-entries': Entry,

        'add-exclusion': Exclusion,
        'revert-exclusions': Exclusion,

        'add-aggregations': Entry,
        # no revert at the moment

    }
    if not main_id and not create:
        out['error']: "Missing ID"
        return out
    if not op:
        out['error']: "Missing operation"
        return out

    cls = classes.get(op)
    if not cls:
        out['error']: "Invalid operation"
        return out

    if main_id and main_id in ids:
        out['error']: "Recursive merging"
        return out

    if main_id:
        try:
            main_object = cls.objects.get(pk=main_id)
        except cls.DoesNotExist:
            out['error'] = "{} does not exist".format(main_id)
            return out
    elif create:
        # TODO: need to catch the exceptions
        main_object = cls.objects.create(**create)
        log_user_operation(user, op, main_object, None)
        out['success'] = "{} created".format(main_object.display_name())
        return out

    other_objects = []
    for oid in ids:
        try:
            obj = cls.objects.get(pk=oid)
            other_objects.append(obj)
        except cls.DoesNotExist:
            out['error'] = "{} does not exist".format(oid)
            return out

    reindex = []
    if op == 'merge-agents' or op == 'merge-entries':
        reindex = cls.merge_records(main_object, other_objects, user=user)
        out['success'] = "Merged"

    elif op == 'add-aggregations':
        if main_object.is_aggregation:
            reindex = cls.aggregate_entries(main_object, other_objects, user=user)
            if reindex:
                out['success'] = "Added"
        else:
            out['error'] = "First item must be an aggregation"

    elif op == 'revert-merged-agents' or op == 'revert-merged-entries':
        reindex = main_object.unmerge(user=user)
        if reindex:
            out['success'] = "Removed merge"
        else:
            out['error'] = "Nothing to do"

    elif op == 'add-translations':
        reindex = cls.translate_records(main_object, other_objects, user=user)
        if reindex:
            out['success'] = "Translations set!"
        else:
            out['error'] = "Nothing to do"

    elif op == 'revert-translations':
        reindex = main_object.untranslate(user=user)
        if reindex:
            out['success'] = "Removed translations"
        else:
            out['error'] = "Nothing to do"

    elif op == 'add-exclusion':
        raise Exception('Not reached')

    elif op == 'revert-exclusions':
        if main_object.user.username == user.username:
            log_user_operation(user, op, main_object, None)
            main_object.delete()
            out['success'] = "Removed"
        else:
            out['error'] = "Cannot do that"

    else:
        raise Exception("Bug! Missing handler for " + op)

    if reindex:
        logger.info("Reindexing")
        indexer = MycorrhizaIndexer(db_path=settings.XAPIAN_DB)
        indexer.index_entries(reindex)
        logger.info(indexer.logs)

    return out
