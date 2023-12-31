import unittest
from .harvest import extract_fields
from .sheets import normalize_records


class HarvestTestCase(unittest.TestCase):
    def setUp(self):
        print("Setting up amwmeta tests")
        pass
    def test_extraction(self):
        rec = extract_fields({
            "title": [ "First", " and second part" ],
            "creator": [ "Pinco", "Pallino" ],
            "subject": [ "Sub1", "Sub2" ],
            "language": [ "eng", "ita", 'lasdfjlasdf' ],
            "date": [ "x 1900 x2023", "x 2012 xxx" ],
            "subtitle": [ "Sub ", " Title " ],
            "description": [ "desc1", "desc2" ],
            "uri_info": [{ "uri": "http://example.com/xx", "label": "XX" }, { "uri": "http://amusewiki.org/xx" }],
            "uri": [ "http://example.com", "http://amusewiki.org" ],
        }, "example.com")
        # print(rec)
        self.assertEqual(rec['title'], "First  and second part")
        self.assertEqual(rec['authors'], [ "Pinco", "Pallino" ])
        self.assertEqual(rec['subjects'], [ "Sub1", "Sub2" ])
        self.assertEqual(rec['languages'], [ "en", "it" ])
        self.assertEqual(rec['subtitle'], "Sub   Title ")
        self.assertEqual(rec['year_first_edition'], "1900")
        self.assertEqual(rec['year_edition'], "2023")
        self.assertEqual(rec['uri'], "http://example.com/xx")
        self.assertEqual(rec['uri_label'], "XX")

        rec2 = extract_fields({
            "title": [ "First", " and second part" ],
            "creator": [ "Pinco", "Pallino" ],
            "subject": [ "xx", "yz" ],
            "language": [ "eng", "ita", "spurious" ],
            "date": [ "x 1999 1900 1800 x2023", "x 2012 xxx" ],
            "subtitle": [ "Sub ", " Title " ],
            "description": [ "desc1 xx ", "desc2 xafasd" ],
            "uri_info": [{ "uri": "http://example.com/xx" }, {
                "uri": "http://amusewiki.org/xx",
                "label": "Y",
                "content_type": "Z"
            }],
            "uri": [ "https://example.com/xx", "http://amusewiki.org/xx" ],
        }, "amusewiki.org")
        self.assertEqual(rec2['year_first_edition'], "1800")
        self.assertEqual(rec2['year_edition'], "2023")
        self.assertEqual(rec2['uri'], "http://amusewiki.org/xx")
        self.assertEqual(rec2['uri_label'], "Y")
        self.assertEqual(rec2['content_type'], "Z")
        self.assertEqual(rec2['languages'], [ "en", "it" ])

        self.assertEqual(rec['checksum'], rec2['checksum'], msg="Checksum ok")
        rec3 = extract_fields({
            "title": [ "Firstx", " and second part" ],
            "creator": [ "Pinco", "Pallino" ],
            "subject": [ "xx", "yz" ],
            "language": [ "en", "it" ],
            "date": [ "x 1999 1900 x2023", "x 2012 xxx" ],
            "subtitle": [ "Sub ", " Title " ],
            "description": [ "desc1 xx ", "desc2 xafasd" ],
            "uri_info": [{ "uri": "http://example.com/xx" }, { "uri": "http://amusewiki.org/xx" }],
            "uri": [ "https://example.com/xx", "http://amusewiki.org/xx" ],
        }, "pippo.org")
        self.assertNotEqual(rec['checksum'], rec3['checksum'], msg="Checksum not matching, title changed")
        self.assertEqual(rec3['uri'], "http://example.com/xx")
        self.assertEqual(rec3['languages'], [ "en", "it" ])
        rec4 = extract_fields({
            "title": [ "Firstx", " and second part" ],
            "creator": [ "Pinco", "Pallino" ],
            "subject": [ "xx", "yz" ],
            "language": [ "enx", "itx" ],
            "date": [ "x 1999 1900 x2023", "x 2012 xxx" ],
            "subtitle": [ "Sub ", " Title " ],
            "description": [ "desc1 xx ", "desc2 xafasd" ],
            "uri_info": [{ "uri": "http://example.com/xx" }, { "uri": "http://amusewiki.org/xx" }],
            "uri": [ "https://example.com/xx", "http://amusewiki.org/xx" ],
        }, "pippo.org")
        self.assertEqual(rec4['languages'], [ "enx", "itx" ])

    def test_sheet(self):
        rec = {
            'authors': 'Giovanni Nikiforos',
            'title': 'Fauna del Mediterraneo',
            'formats': '',
            'pubdate': '2002-07-15T21:42:54+02:00',
            'publisher': 'Giunti Editore',
            'comments': "Una guida completa per conoscere e saper riconoscere le molteplici varietà di forme viventi che animano il Mar Mediterraneo. Un'opera esaustiva che tratta più di 3.500 specie, tutte rappresentate e illustrate a colori, con chiavi di identificazione che rendono semplice e immediata l'identificazione di ciascun animale, chiamato con il proprio nome scientifico quanto con il più comune nome italiano.",
            'cover': '',
            'timestamp': '2023-07-09T21:42:47+02:00',
            'size': '',
            'isbn': '9788809062979',
            'identifiers': 'google:_vRFPQAACAAJ,isbn:9788809062979',
            'languages': 'ita',
            'library_name': 'Elenco libri cartacei',
            'author_sort': 'Nikiforos, Giovanni',
            'title_sort': 'Fauna del Mediterraneo',
            'series': '',
            'series_index': '1.0',
            'tags': 'Animals, Biologia, Marine Life, Nature',
            'rating': '',
            'id': '1',
            'uuid': '65ea26c3-1cbb-4308-8eb2-a0daaa198e15',
            '#isbn': '9788809062979',
            '#formats': '',
        }
        got = normalize_records('calibre', [rec])[0]
        # print(got)
        self.assertEqual(got['language'], ['ita'])
        oai = extract_fields(got, 'pippo.org')
        self.assertEqual(oai['languages'][0], 'it')
        self.assertIn('checksum', oai)
