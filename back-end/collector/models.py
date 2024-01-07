from django.db import models
from datetime import datetime
from amwmeta.harvest import harvest_oai_pmh, extract_fields
from urllib.parse import urlparse
from datetime import datetime, timezone
from django.db import transaction
from amwmeta.xapian import MycorrhizaIndexer
from django.contrib.auth.models import User
import logging
from amwmeta.sheets import parse_sheet, normalize_records
import random
import requests
import re

logger = logging.getLogger(__name__)

class Library(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255,
                          blank=True,
                          null=True)
    public = models.BooleanField(default=False, null=False)
    active = models.BooleanField(default=True, null=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Libraries"

class Site(models.Model):
    OAI_DC = "oai_dc"
    MARC21 = "marc21"
    OAI_PMH_METADATA_FORMATS = [
        (OAI_DC, "Dublin Core"),
        (MARC21, "MARC XML"),
    ]
    SITE_TYPES = [
        ('amusewiki', "Amusewiki"),
        ('generic', "Generic OAI-PMH"),
        ('csv', "CSV Upload"),
    ]
    library = models.ForeignKey(Library,
                                null=False,
                                on_delete=models.CASCADE,
                                related_name="sites")
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    last_harvested = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    oai_set = models.CharField(max_length=64,
                               blank=True,
                               null=True)
    oai_metadata_format = models.CharField(max_length=32,
                                           null=True,
                                           choices=OAI_PMH_METADATA_FORMATS)
    site_type = models.CharField(max_length=32, choices=SITE_TYPES, default="generic")
    active = models.BooleanField(default=True, null=False)
    amusewiki_formats = models.JSONField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} ({} - {})".format(self.title, self.site_type, self.url)

    def last_harvested_zulu(self):
        dt = self.last_harvested
        if dt:
            # clone
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return None

    def hostname(self):
        return urlparse(self.url).hostname

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
                self.save()
            else:
                logger.debug("GET {0} returned {1}".format(r.url, r.status_code))

    def harvest(self, force):
        self.update_amusewiki_formats()
        url = self.url
        hostname = self.hostname()
        now = datetime.now(timezone.utc)
        opts = {
            "metadataPrefix": self.oai_metadata_format,
        }
        last_harvested = self.last_harvested_zulu()
        logger.debug([ force, last_harvested ])
        if last_harvested and not force:
            opts['from'] = last_harvested
        if self.oai_set:
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

            entry = self.process_harvested_record(record, aliases, now)
            if entry:
                xapian_records.append(entry.id)
        # and index
        self.index_harvested_records(xapian_records, force, now)

    def index_harvested_records(self, xapian_records, force, now):
        indexer = MycorrhizaIndexer()
        all_ids = list(set(xapian_records))
        logger.debug("Indexing " + str(all_ids))
        for id in all_ids:
            ientry = Entry.objects.get(pk=id)
            indexer.index_record(ientry.indexing_data())

        logs = indexer.logs
        if logs:
            msg = "Total indexed: " + str(len(logs))
            logger.info(msg)
            logs.append(msg)
            self.last_harvested = now
            self.save()
            self.harvest_set.create(datetime=now, logs="\n".join(logs))

    def process_harvested_record(self, record, aliases, now):
        authors = []
        languages = []
        try:
            for author in record.pop('authors', []):
                obj, was_created = Agent.objects.get_or_create(name=aliases['author'].get(author, author))
                authors.append(obj)
        except KeyError:
            pass

        try:
            for language in record.pop('languages', []):
                lang = language[0:3]
                obj, was_created = Language.objects.get_or_create(code=aliases['language'].get(lang, lang))
                languages.append(obj)
        except KeyError:
            pass

        # logger.debug(record)
        identifier = record.pop('identifier')
        opr_attributes = [
            'full_data',
            'uri',
            'uri_label',
            'content_type',
            'shelf_location_code',
            'material_description',
            'year_edition',
            'year_first_edition',
            'description',
        ]
        opr_attrs = { x: record.pop(x, None) for x in opr_attributes }
        opr_attrs['datetime'] = now
        opr, opr_created = self.datasource_set.update_or_create(
            oai_pmh_identifier=identifier,
            defaults=opr_attrs
        )
        for f in [ 'title', 'subtitle' ]:
            f_value = record.get(f)
            if f_value and len(f_value) > 250:
                f_value = f_value[0:250] + '...'
            record[f] = aliases[f].get(f_value, f_value)

        # if the OAI-PMH record has already a entry attached from a
        # previous run, that's it, just update it.
        entry = opr.entry
        if record.pop('deleted'):
            opr.delete()
            return entry

        if not entry:
            # check if there's already a entry with the same checksum.
            try:
                entry = Entry.objects.get(checksum=record['checksum'])
            except Entry.DoesNotExist:
                entry = Entry.objects.create(**record)
            opr.entry = entry
            opr.save()

        # update the entry and assign the many to many
        for attr, value in record.items():
            setattr(entry, attr, value)

        entry.authors.set(authors)
        entry.languages.set(languages)
        entry.save()
        return entry



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

    @classmethod
    def merge_records(cls, canonical, aliases):
        canonical.canonical_agent = None
        canonical.save()
        reindex_agents = aliases[:]
        reindex_agents.append(canonical)
        for aliased in aliases:
            aliased.canonical_agent = canonical
            aliased.save()
            for va in aliased.variant_agents.all():
                va.canonical_agent = canonical
                va.save()
                reindex_agents.append(va)
        entries = []
        for agent in reindex_agents:
            for entry in agent.authored_entries.all():
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

    class Meta:
        verbose_name_plural = "Entries"

    def __str__(self):
        return self.title

    def display_dict(self):
        out = {}
        for f in [ 'id', 'title', 'subtitle' ]:
            out[f] = getattr(self, f)
        return out

    def display_data(self, library_ids=[]):
        indexed = self.indexed_data
        record = self.display_dict()
        record['authors'] = indexed.get('creator')
        data_sources = []
        for ds in indexed.get('data_sources'):
            # only the sites explicitely set in the argument
            if ds['library_id'] in library_ids:
                if ds['site_type'] == 'amusewiki':
                    ds['downloads'] = Site.objects.get(pk=ds['site_id']).amusewiki_formats
                data_sources.append(ds)
        record['data_sources'] = data_sources

        original = self.original_entry
        if original:
            record['original_entry'] = original.display_dict()
        record['translations'] = [ tr.display_dict() for tr in self.translations.all() ]

        return record

    def indexing_data(self):
        # we index the entries
        data_source_records = []

        if self.canonical_entry:
            data_source_records = []
        else:
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
        for topr in data_source_records:
            site = topr.site
            library = site.library
            dsd = {
                "data_source_id": topr.id,
                "identifier": topr.oai_pmh_identifier,
                "uri": topr.uri,
                "uri_label": topr.uri_label,
                "content_type": topr.content_type,
                "shelf_location_code": topr.shelf_location_code,
                "public": library.public,
                "site_name": site.title,
                "site_id": site.id,
                "site_type": site.site_type,
                "library_id" : library.id,
                "library_name": library.name,
            }
            if library.active and library.public:
                record_is_public = True
            xapian_data_sources.append(dsd)

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

        xapian_record = {
            # these are the mapped ones
            "title": [ { "id": self.id, "value": self.title }, { "id": self.id, "value": self.subtitle } ],
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
        }
        # logger.debug(xapian_record)
        if len(xapian_record['library']) == 1:
            xapian_record['unique_source'] = xapian_record['library'][0]['id']

        self.indexed_data = xapian_record
        self.save()
        return xapian_record

    @classmethod
    def merge_records(cls, canonical, aliases):
        canonical.canonical_entry = None
        canonical.save()
        reindex = aliases[:]
        for aliased in aliases:
            aliased.canonical_entry = canonical
            aliased.save()
            # update the current variant entries
            for ve in aliased.variant_entries.all():
                ve.canonical_entry = canonical
                ve.save()
                reindex.append(ve)
        logger.debug(reindex)
        # update the translations
        Entry.objects.filter(original_entry__in=reindex).update(original_entry=canonical)
        reindex.append(canonical)
        return reindex


# the OAI-PMH records will keep the URL of the record, so a entry can
# have multiple ones because it's coming from more sources.

# DataSource
class DataSource(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    oai_pmh_identifier = models.CharField(max_length=2048)
    datetime = models.DateTimeField()
    full_data = models.JSONField()

    entry = models.ForeignKey(Entry, null=True, on_delete=models.SET_NULL)

    description = models.TextField(null=True)
    year_edition = models.IntegerField(null=True)
    year_first_edition = models.IntegerField(null=True)

    # if digital, provide the url
    uri = models.URLField(max_length=2048, null=True)
    uri_label = models.CharField(max_length=2048, null=True)
    content_type = models.CharField(max_length=128, null=True)
    # if this is the real book, if it exists: phisical description and call number
    material_description = models.TextField(null=True)
    shelf_location_code = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['site', 'oai_pmh_identifier'], name='unique_site_oai_pmh_identifier'),
        ]
    def __str__(self):
        return self.oai_pmh_identifier

    def amusewiki_base_url(self):
        site = self.site
        if site.site_type == 'amusewiki':
            return re.sub(r'((\.[a-z0-9]+)+)$',
                          '',
                          self.uri)
        else:
            return None

    def get_remote_file(self, ext):
        amusewiki_url = self.amusewiki_base_url()
        if amusewiki_url:
            logger.debug("AMW url is " + amusewiki_url)
            return requests.get(amusewiki_url + ext)
        else:
            return None

    def full_text(self):
        amusewiki_url = self.amusewiki_base_url()
        if amusewiki_url:
            r = requests.get(amusewiki_url + '.bare.html')
            if r.status_code == 200:
                r.encoding = 'UTF-8'
                return r.text
        else:
            return None

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
    return "spreadsheets/{0}-{1}.csv".format(int(datetime.now().timestamp()),
                                             "".join(random.choice(choices) for i in range(20)))

class SpreadsheetUpload(models.Model):
    CSV_TYPES = [
        ('calibre', 'Calibre'),
    ]
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
    csv_type = models.CharField(max_length=32, choices=CSV_TYPES)
    replace_all = models.BooleanField(default=False, null=False)
    processed = models.DateTimeField(null=True, blank=True)

    def validate_csv(self):
        return parse_sheet(self.csv_type, self.spreadsheet.path, sample=True)

    def process_csv(self):
        now = datetime.now(timezone.utc)
        records = normalize_records(self.csv_type,
                                    parse_sheet(self.csv_type, self.spreadsheet.path))
        site = self.site
        hostname = site.hostname()
        aliases = site.record_aliases()
        xapian_records = []
        if self.replace_all:
            # see above in site.harvest()
            xapian_records = [ i.entry_id for i in site.datasource_set.all() ]
            site.datasource_set.all().delete()

        logger.debug("Reindexing: {}".format(xapian_records))
        for full in records:
            logger.debug(full)
            record = extract_fields(full, hostname)
            if full.get('identifier'):
                record['identifier'] = 'ss:{}:{}'.format(hostname, full['identifier'][0])
            record['full_data'] = full
            record['deleted'] = False
            entry = site.process_harvested_record(record, aliases, now)
            if entry:
                xapian_records.append(entry.id)
        site.index_harvested_records(xapian_records, self.replace_all, now)
        self.processed = now
        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    libraries = models.ManyToManyField(Library)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
