from django.test import TestCase
from .models import Entry, Agent, Site, DataSource
from datetime import datetime, timezone

class AliasesTestCase(TestCase):
    def setUp(self):
        pinco = Agent.objects.create(name="Pinco Pallino")
        pincu = Agent.objects.create(name="Pincic Pallinic")
        pinco.canonical_agent = pincu
        pinco.save()
        entrya = Entry.objects.create(title="Pizzaa",
                                      year_edition="1900",
                                      checksum="XX")
        entrya.authors.set([ pinco ])
        entryb = Entry.objects.create(title="Pizzab",
                                      year_edition="1900",
                                      checksum="XX")
        entryb.authors.set([ pincu ])
        entrya.canonical_entry = entryb
        entrya.save()
    def test_aliases_ok(self):
        for entry in Entry.objects.all():
            # print(entry.indexing_data())
            xapian = entry.indexing_data()
            print(xapian)
            # self.assertEqual(xapian['title'][0], 'Pizzab')
            self.assertEqual(xapian['creator'][0]['value'], 'Pincic Pallinic')
            self.assertEqual(xapian['date'][0]['value'], 1900)

class SitePrivateTestCase(TestCase):
    def setUp(self):
        sources = []
        counter = 0
        entry = Entry.objects.create(
            title="Pizza",
            year_edition="1900",
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
                site = Site.objects.create(
                    title=name,
                    url="https://name.org",
                    public=public,
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
        self.assertEqual(entry.indexing_data()['public'], True)

        Site.objects.filter(public=True, active=True).update(active=False)
        self.assertEqual(entry.indexing_data()['public'], False)

        Site.objects.filter(title="public-active").update(active=True)
        self.assertEqual(entry.indexing_data()['public'], True)

        Site.objects.filter(title="public-active").update(public=False)
        self.assertEqual(entry.indexing_data()['public'], False)

