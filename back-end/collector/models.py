from django.db import models
from datetime import datetime
from amwmeta.harvest import harvest_oai_pmh, extract_fields
from urllib.parse import urlparse
from datetime import datetime, timezone
from django.db import transaction
from amwmeta.xapian import MycorrhizaIndexer
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class Site(models.Model):
    OAI_DC = "oai_dc"
    MARC21 = "marc21"
    OAI_PMH_METADATA_FORMATS = [
        (OAI_DC, "Dublin Core"),
        (MARC21, "MARC XML"),
    ]
    SITE_TYPES = [
        ('amusewiki', "Amusewiki"),
        ('generic', "Generic"),
    ]
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)
    last_harvested = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(blank=True)
    oai_set = models.CharField(max_length=64, blank=True)
    oai_metadata_format = models.CharField(max_length=32,
                                           choices=OAI_PMH_METADATA_FORMATS,
                                           default=OAI_DC)
    site_type = models.CharField(max_length=32, choices=SITE_TYPES, default="generic")
    public = models.BooleanField(default=True, null=False)
    active = models.BooleanField(default=True, null=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def last_harvested_zulu(self):
        dt = self.last_harvested
        if dt:
            # clone
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            return None

    def hostname(self):
        return urlparse(self.url).hostname

    def harvest(self, force):
        url = self.url
        hostname = urlparse(url).hostname
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

        if force:
            self.datasource_set.all().delete()

        records = harvest_oai_pmh(url, opts)
        xapian_records = []
        logs = []
        aliases = {
            "author": {},
            "subject": {},
            "language": {},
        }
        for al in self.namealias_set.all():
            aliases[al.field_name][al.value_name] = al.value_canonical

        logger.debug(aliases)
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

            # logger.debug(record)
            authors = []
            subjects = []
            languages = []
            # handle the 3 lists
            try:
                for author in record.pop('authors', []):
                    obj, was_created = Agent.objects.get_or_create(name=aliases['author'].get(author, author))
                    authors.append(obj)
            except KeyError:
                pass

            try:
                for subject in record.pop('subjects', []):
                    obj, was_created = Subject.objects.get_or_create(name=aliases['subject'].get(subject, subject))
                    subjects.append(obj)
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
            ]
            opr_attrs = { x: record.pop(x, None) for x in opr_attributes }
            opr_attrs['datetime'] = now
            opr, opr_created = self.datasource_set.update_or_create(
                oai_pmh_identifier=identifier,
                defaults=opr_attrs
            )
            for f_limit in [ 'title', 'subtitle' ]:
                try:
                    if record[f_limit]:
                        if len(record[f_limit]) > 250:
                            record[f_limit] = record[f_limit][0:250] + '...'
                except KeyError:
                    pass

            # if the OAI-PMH record has already a entry attached from a
            # previous run, that's it, just update it.
            entry = opr.entry

            if record.pop('deleted'):
                opr.delete()
                if entry:
                    xapian_records.append(entry.id)
                continue

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
            entry.subjects.set(subjects)
            entry.authors.set(authors)
            entry.languages.set(languages)
            entry.save()
            xapian_records.append(entry.id)

        indexer = MycorrhizaIndexer()
        if force:
            logger.debug("Removing all related entries in Xapian db")
            indexer.db.delete_document("XH{}".format(self.id))

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

class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

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
    description = models.TextField(null=True)
    authors = models.ManyToManyField(Agent, related_name="authored_entries")
    subjects = models.ManyToManyField(Subject)
    languages = models.ManyToManyField(Language)
    year_edition = models.IntegerField(null=True)
    year_first_edition = models.IntegerField(null=True)
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

    class Meta:
        verbose_name_plural = "Entries"

    def __str__(self):
        return self.title

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
            dsd = {
                "identifier": topr.oai_pmh_identifier,
                "uri": topr.uri,
                "uri_label": topr.uri_label,
                "content_type": topr.content_type,
                "shelf_location_code": topr.shelf_location_code,
                "public": site.public,
                "site_name": site.title,
                "site_id": site.id,
            }
            if site.active and site.public:
                record_is_public = True
            xapian_data_sources.append(dsd)

        entry_sites = {}
        for topr in data_source_records:
            if not entry_sites.get(topr.site_id):
                entry_site = topr.site
                entry_sites[topr.site_id] = {
                    "id": entry_site.id,
                    "value": entry_site.title,
                }

        xapian_record = {
            # these are the mapped ones
            "title": [ { "id": self.id, "value": self.title }, { "id": self.id, "value": self.subtitle } ],
            "creator": authors,
            "subject":  [ { "id": s.id, "value": s.name } for s in self.subjects.all() ],
            "date":     [ { "id": d, "value": d } for d in [ self.year_edition ] if d ],
            "language": [ { "id": l.code, "value": l.code } for l in self.languages.all() ],
            "site": list(entry_sites.values()),
            "description": [ { "id": "d" + str(self.id), "value": s } for s in [ self.description ] if s ],
            "data_sources": xapian_data_sources,
            "entry_id": self.id,
            "public": record_is_public,
            "last_modified": self.last_modified.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "unique_source": 0,
        }
        if len(xapian_record['site']) == 1:
            xapian_record['unique_source'] = xapian_record['site'][0]['id']

        self.indexed_data = xapian_record
        self.save()
        return xapian_record

    @classmethod
    def merge_records(cls, canonical, aliases):
        canonical.canonical_entry = None
        canonical.save()
        reindex = aliases[:]
        reindex.append(canonical)
        for aliased in aliases:
            aliased.canonical_entry = canonical
            aliased.save()
            # update the current variant entries
            for ve in aliased.variant_entries.all():
                ve.canonical_entry = canonical
                ve.save()
                reindex.append(ve)
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

class NameAlias(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    field_name = models.CharField(
        max_length=32,
        choices=[
            ('author', 'Author'),
            ('subject', 'Subject'),
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
    exclude_site   = models.ForeignKey(Site,  null=True, on_delete=models.SET_NULL)
    exclude_author = models.ForeignKey(Agent, null=True, on_delete=models.SET_NULL)
    exclude_entry  = models.ForeignKey(Entry, null=True, on_delete=models.SET_NULL)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    def as_xapian_queries(self):
        queries = []
        if self.exclude_site:
            queries.append(('site', self.exclude_site.id))
        if self.exclude_author:
            queries.append(('creator', self.exclude_author.id))
        if self.exclude_entry:
            queries.append(('entry', self.exclude_entry.id))
        return queries
