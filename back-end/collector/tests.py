from pathlib import Path
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import User, Entry, Agent, Site, DataSource, Library, Language, AggregationEntry
from datetime import datetime, timezone
from amwmeta.harvest import extract_fields
from amwmeta.xapian import search
from .tasks import xapian_index_records
import copy
import pprint
import shutil
pp = pprint.PrettyPrinter(indent=4)

xapian_test_db = Path('xapian', 'tests')
if xapian_test_db.is_dir():
    print("Removing existing " + str(xapian_test_db))
    shutil.rmtree(str(xapian_test_db))
xapian_test_db.mkdir(parents=True)


@override_settings(XAPIAN_DB=str(xapian_test_db))
class ViewsTestCase(TestCase):
    def setUp(self):
        password = 'password'
        User.objects.create_superuser('admin', 'admin@test.com', password)

    def test_api_create(self):
        data = {
            "value": "test",
        }
        # make sure unauthorized can't create
        res = self.client.post(reverse('api_create', args=['aggregation']),
                               data=data,
                               content_type="application/json")
        self.assertEqual(res.status_code, 302)
        res = self.client.post(reverse('api_create', args=['agent']),
                               data=data,
                               content_type="application/json")
        self.assertEqual(res.status_code, 302)

        # login and create an aggregation
        self.client.login(username="admin", password="password")

        res = self.client.post(reverse('api_create', args=['aggregation']),
                               data={"value": "Pizzosa"},
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['created']['type'], 'aggregation')
        eid = res.json()['created']['id']

        # which is an entry
        agg = Entry.objects.get(pk=eid)
        self.assertTrue(agg.checksum)
        self.assertTrue(agg.is_aggregation)
        self.assertEqual(agg.title, "Pizzosa")

        data = { "value": "test agent for merging" }
        res = self.client.post(reverse('api_create', args=['agent']),
                               data=data,
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['created']['type'], 'agent')
        aid = res.json()['created']['id']
        author = Agent.objects.get(pk=aid)
        self.assertEqual(author.name, data['value'])

        # this is a wrong URL /create/pippo
        res = self.client.post(reverse('api_create', args=['pippo']),
                               data=data,
                               content_type="application/json")
        self.assertTrue(res.json()['error'])

        entry = Entry.objects.create(title="A test title", is_aggregation=False);
        library = Library.objects.create(
            name="Test library",
            public=True,
            active=True,
        )
        site = Site.objects.create(
            library=library,
            title="Test site",
            url="https://example.org",
            active=True,
        )
        identifier = "oai:test:disregard"
        datasource = DataSource.objects.create(
            site=site,
            oai_pmh_identifier=identifier,
            datestamp=datetime.now(timezone.utc),
            entry=entry,
            full_data={},
        )

        for x in (1, 2, 3):
            data = [ { "id": agg.id }, { "id": entry.id } ]
            res = self.client.post(reverse('api_set_aggregated'),
                                   data=data,
                                   content_type="application/json")
            # pp.pprint(res.json())
            found_rel = AggregationEntry.objects.get(aggregated_id=entry.id, aggregation_id = eid)
            self.assertTrue(found_rel)
            xapian_index_records([agg.id, entry.id])

            res = self.client.get(reverse('api_search'), { "query": "Pizzosa" })
            # pp.pprint(res.json())
            self.assertEqual(res.json()['total_entries'], 2, "Found the aggregated and the aggregation")

@override_settings(XAPIAN_DB=str(xapian_test_db))
class AliasesTestCase(TestCase):
    def setUp(self):
        pinco = Agent.objects.create(name="Pinco Pallino")
        pincu = Agent.objects.create(name="Pincic Pallinic")
        pinco.canonical_agent = pincu
        pinco.save()
        entrya = Entry.objects.create(title="Pizzaa",
                                      checksum="XX")
        entrya.authors.set([ pinco ])
        entryb = Entry.objects.create(title="Pizzab",
                                      checksum="XX")
        entryb.authors.set([ pincu ])
        entrya.canonical_entry = entryb
        entrya.save()
    def test_aliases_ok(self):
        for entry in Entry.objects.all():
            # print(entry.indexing_data())
            xapian = entry.indexing_data()
            # print(xapian)
            # self.assertEqual(xapian['title'][0], 'Pizzab')
            self.assertEqual(xapian['creator'][0]['value'], 'Pincic Pallinic')

@override_settings(XAPIAN_DB=str(xapian_test_db))
class SitePrivateTestCase(TestCase):
    def setUp(self):
        sources = []
        counter = 0
        entry = Entry.objects.create(
            title="Pizza",
            checksum="XX",
        )
        for public in (True, False):
            counter += 1
            if public:
                name = "public"
            else:
                name =" private"

            for active in (True, False):
                if active:
                    name = name + "-active"
                else:
                    name = name + "-inactive"
                library = Library.objects.create(
                    name=name,
                    public=public,
                    active=active,
                )
                site = Site.objects.create(
                    library=library,
                    title=name,
                    url="https://name.org",
                    active=active,
                )
                identifier = "oai:" + name + str(counter)
                datasource = DataSource.objects.create(
                    site=site,
                    oai_pmh_identifier=identifier,
                    datestamp=datetime.now(timezone.utc),
                    entry=entry,
                    full_data={},
                )
    def test_indexing_data(self):
        entry = Entry.objects.first()

        # pp.pprint(entry.indexing_data())
        self.assertEqual(entry.indexing_data()['unique_source'], 0)
        self.assertEqual(entry.indexing_data()['public'], True)

        Library.objects.filter(public=True, active=True).update(active=False)
        self.assertEqual(entry.indexing_data()['public'], False)

        Library.objects.filter(name="public-active").update(active=True)
        self.assertEqual(entry.indexing_data()['public'], True)

        Library.objects.filter(name="public-active").update(public=False)
        self.assertEqual(entry.indexing_data()['public'], False)

        self.assertEqual(entry.indexing_data()['unique_source'], 0)


@override_settings(XAPIAN_DB=str(xapian_test_db))
class UniqueSiteTestCase(TestCase):
    def setUp(self):
        library = Library.objects.create(
            name="Test",
            url="https://name.org",
            public=True,
            active=True,
        )
        site = Site.objects.create(
            library=library,
            title="Test",
            url="https://name.org",
        )
        entry = Entry.objects.create(
            title="Pizza",
            checksum="XX",
        )
        datasource = DataSource.objects.create(
            site=site,
            oai_pmh_identifier="XX",
            datestamp=datetime.now(timezone.utc),
            entry=entry,
            full_data={},
        )
    def test_unique_source(self):
        entry = Entry.objects.first()
        site = Site.objects.first()
        self.assertEqual(entry.indexing_data()['unique_source'], site.id)

@override_settings(XAPIAN_DB=str(xapian_test_db))
class AggregationProcessingTestCase(TestCase):
    def setUp(self):
        library = Library.objects.create(
            name="Test",
            url="https://name.org",
            public=True,
            active=True,
        )
        site = Site.objects.create(
            library=library,
            title="Test",
            url="https://name.org",
        )
    def test_processing(self):
        site = Site.objects.first()
        marc = {'added_entry_personal_name': [],
                'added_entry_place_publisher_date': [],
                'added_entry_relator_term': [],
                'added_entry_title': [],
                'agent_details': [{'name': 'Pinco Pallino', 'relator_term': 'author'},
                                  {'name': 'Marco Pessotto', 'relator_term': 'author'},
                                  {'name': 'Tizio Caio Sempronio', 'relator_term': 'author'}],
                'aggregation': [{'issue': '2',
                                 'item_identifier': 'test-1',
                                 'linkage': 'https://staging.amusewiki.org/aggregation/test-1',
                                 'name': 'First Test',
                                 'order': '1',
                                 'place_date_publisher': 'A Nice place 2023'},
                                {'issue': '2',
                                 'item_identifier': 'test-2',
                                 'linkage': 'https://staging.amusewiki.org/aggregation/test-2',
                                 'name': 'Second Test',
                                 'order': '1',
                                 'place_date_publisher': 'Another place'}],
                'content_type': ['text'],
                'country_of_publishing': [],
                'creator': ['Pinco Pallino', 'Marco Pessotto', 'Tizio Caio Sempronio'],
                'cumulative_index_aids_note': [],
                'date': ['2022'],
                'description': ['Everything you have to know about the Text::Amuse markup. '
                                'Last updated for version 1.81 (1.81 March 29, 2022).',
                                'Catalog Number: x145'],
                'dissertation_note': [],
                'edition_statement': [],
                'former_title': [],
                'general_note': [],
                'identifier': [],
                'isbn': [],
                'issn': [],
                'issuing_body_note': [],
                'koha_uri': [],
                'language': ['en'],
                'national_bibliography_number': [],
                'numbering_peculiarities__note': [],
                'material_description': [],
                'place_date_of_publication_distribution': ['2022'],
                'preceding_entry_place_publisher_date': [],
                'preceding_entry_relationship_information': [],
                'preceding_entry_title': [],
                'publisher': [],
                'rights': [],
                'serial_enumeration_caption': [],
                'shelf_location_code': ['SLC-123'],
                'subject': ['doc', 'howto'],
                'subtitle': ['The writer’s guide'],
                'supplement_relationship_information': [],
                'terms_of_availability': [],
                'title': ['The Text::Amuse markup manual'],
                'title_for_search': [],
                'trade_price_currency': [],
                'trade_price_value': ['43'],
                'uri': ['https://staging.amusewiki.org/library/manual'],
                'uri_info': [{'content_type': 'text/html',
                              'label': 'Landing page',
                              'uri': 'https://staging.amusewiki.org/library/manual'}],
                'with_note': [],
                'wrong_issn': []}
        hostname = 'staging.amusewiki.org'
        record = extract_fields(marc, hostname)
        record['identifier'] = 'oai:{}:{}'.format(hostname, 'pizza-pizza')
        record['full_data'] = record
        record['deleted'] = False
        # twice so we test the idempotency
        site.process_harvested_record(copy.deepcopy(record), None, datetime.now(timezone.utc))
        site.process_harvested_record(copy.deepcopy(record), None, datetime.now(timezone.utc))
        self.assertEqual(Agent.objects.count(), 3)
        self.assertEqual(Language.objects.count(), 1)
        self.assertEqual(Entry.objects.count(), 3,
                         "One entry for the article and two for the aggregations")
        self.assertEqual(DataSource.objects.count(), 3,
                         "One DS for the article and two for the aggregations")
        self.assertEqual(Entry.objects.filter(is_aggregation=True).count(), 2)
        self.assertEqual(DataSource.objects.filter(is_aggregation=True).count(), 2)
        # for entry in Entry.objects.filter(is_aggregation=True).all():
            # pp.pprint(entry.indexing_data())


@override_settings(XAPIAN_DB=str(xapian_test_db))
class PdfEextractionTestCase(TestCase):
    def setUp(self):
        library = Library.objects.create(name="Test", public=True, active=True)
        site = Site.objects.create(
            library=library,
            site_type="calibretree",
            tree_path="testfiles/calibre-test",
        )
    def test_pdf_extraction(self):
        # print("Testing PDF extraction")
        site = Site.objects.first()
        self.assertEqual(site.site_type, "calibretree")
        self.assertEqual(site.tree_path, "testfiles/calibre-test")
        site.harvest()
        ds = DataSource.objects.first()
        self.assertEqual(ds.site_id, site.id)
        self.assertIsNotNone(ds.site)
        self.assertIn("backcompatibility issues", site.datasource_set.first().full_text())
