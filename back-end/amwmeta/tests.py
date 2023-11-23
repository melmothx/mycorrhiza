import unittest
from .harvest import extract_fields


class HarvestTestCase(unittest.TestCase):
    def setUp(self):
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
