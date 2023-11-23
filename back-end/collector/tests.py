from django.test import TestCase
from .models import Entry, Agent

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
            self.assertEqual(xapian['date'][0]['value'], '1900')

