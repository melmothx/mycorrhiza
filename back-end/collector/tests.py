from django.test import TestCase
from .models import Entry, Agent, Site, DataSource, Library, Language
from datetime import datetime, timezone

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
                    datetime=datetime.now(timezone.utc),
                    entry=entry,
                    full_data={},
                )
    def test_indexing_data(self):
        entry = Entry.objects.first()

        self.assertEqual(entry.indexing_data()['unique_source'], 0)
        self.assertEqual(entry.indexing_data()['public'], True)

        Library.objects.filter(public=True, active=True).update(active=False)
        self.assertEqual(entry.indexing_data()['public'], False)

        Library.objects.filter(name="public-active").update(active=True)
        self.assertEqual(entry.indexing_data()['public'], True)

        Library.objects.filter(name="public-active").update(public=False)
        self.assertEqual(entry.indexing_data()['public'], False)

        self.assertEqual(entry.indexing_data()['unique_source'], 0)


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
            datetime=datetime.now(timezone.utc),
            entry=entry,
            full_data={},
        )
    def test_unique_source(self):
        entry = Entry.objects.first()
        site = Site.objects.first()
        self.assertEqual(entry.indexing_data()['unique_source'], site.id)

class AggregationProcessingTestCase(TestCase):
    def setUp(self):
        print("Setting up aggregation testing")
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
        record = {
            'aggregations': [{
                'issue': '1',
                'name': 'Pizza',
                'order': '21',
                'place_date_publisher': 'March 19-April 1, 1970',
                'full_aggregation_name': 'Pizza',
                'identifier': 'aggregation:name.org:Pizza:1',
            }],
            'authors': ['Pinco Pallino'],
            'checksum': 'b173c30f6ca88428bdba283dbfa4aa182bc297d9de3158fc95be368f22b60969',
            'content_type': 'text/html',
            'description': 'Random desc',
            'languages': ['en'],
            'subtitle': '',
            'title': 'My Article',
            'uri': 'https://amusewiki.org/library/manual',
            'uri_label': 'Landing page',
            'year_edition': '2022',
            'identifier': 'xyz',
            'full_data': {},
            'deleted': False,
        }
        site.process_harvested_record(record, None, datetime.now(timezone.utc))
        self.assertEqual(Agent.objects.count(), 1)
        self.assertEqual(Language.objects.count(), 1)
        self.assertEqual(Entry.objects.count(), 2, "One for the article and one for the aggregation")
        self.assertEqual(DataSource.objects.count(), 2, "One for the article and one for the aggregation")
