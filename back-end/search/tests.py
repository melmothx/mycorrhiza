from django.test import TestCase
from search.models import Work, Agent

class AliasesTestCase(TestCase):
    def setUp(self):
        pinco = Agent.objects.create(name="Pinco Pallino")
        pincu = Agent.objects.create(name="Pincic Pallinic")
        pinco.canonical_agent = pincu
        pinco.save()
        worka = Work.objects.create(title="Pizzaa",
                                    checksum="XX")
        worka.authors.set([ pinco ])
        workb = Work.objects.create(title="Pizzab",
                                    checksum="XX")
        workb.authors.set([ pincu ])
        worka.canonical_work = workb
        worka.save()
    def test_aliases_ok(self):
        for work in Work.objects.all():
            # print(work.indexing_data())
            xapian = work.indexing_data()
            print(xapian)
            # self.assertEqual(xapian['title'][0], 'Pizzab')
            self.assertEqual(xapian['creator'][0], 'Pincic Pallinic')

