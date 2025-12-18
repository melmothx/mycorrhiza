import requests
from lxml import html,etree
import logging
import pprint
import sys
import re
import hashlib
from urllib.parse import urlparse
from datetime import datetime,timezone

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)

class SpipIndexer:
    def __init__(self, base_url, max_id=2000):
        self.max_id = max_id
        self.base_url = base_url
        self.hostname = urlparse(base_url).hostname
        self.records = []
        self.ua = requests.Session()
        self.ua.headers.update({ 'User-Agent': 'Mycorrhiza 1.0 https://github.com/melmothx/mycorrhiza' })

    def harvest(self, force=False):
        urls = []
        if force:
            for i in range(int(self.max_id)):
                urls.append("{}/article{}.html".format(self.base_url, i + 1))
        else:
            r = self.ua.get("{}/spip.php?page=backend".format(self.base_url))
            if r.status_code == 200:
                root = etree.fromstring(r.content)
                for el in root.xpath("//link"):
                    urls.append(el.text)
        mapping = [
            ('dc.identifier', 'identifier'),
            ('dc.title', 'title'),
            ('dc.date.created', 'date'),
            ('dc.publisher', 'publisher'),
            ('dc.language', 'language'),
            ('dc.description', 'description'),
            ('dc.creator', 'creator'),
            ('dc.subject', 'description'),
            ('dc.date.modified', 'datestamp'),
            # these relations are too broad
            # ('dc.relation', 'aggregation'),
        ]
        for url in urls:
            good = re.fullmatch(r'.*/article([0-9]+)\.html', url)
            if good:
                identifier = good.group(1)
                r = self.ua.get(url)
                if r.status_code == 200:
                    doc = html.fromstring(r.content)
                    out = {
                        'identifier': [ identifier ],
                        'uri_info': [{
                            "uri": url,
                            "content_type": "text/html",
                            "label": "URL",
                        }],
                    }
                    for tag in mapping:
                        tagname, dest = tag
                        if dest not in out:
                            out[dest] = []
                        for el in doc.xpath("//meta[@name='{}']".format(tagname)):
                            text = el.attrib.get('content')
                            if text:
                                out[dest].append(text)
                    if out['title']:
                        # out['aggregation'] = [ { "name": agg } for agg in out['aggregation'] ]
                        # if out['aggregation']:
                        #     out['aggregation_objects'] = []
                        #     for agg in out['aggregation']:
                        #         asha = hashlib.sha256()
                        #         asha.update(agg['name'].encode())
                        #         agg['checksum'] = asha.hexdigest()
                        #         out['aggregation_objects'].append({
                        #             'order': None,
                        #             'data': {
                        #                 'title': agg['name'],
                        #                 "checksum": agg['checksum'],
                        #                 'identifier': 'aggregation:{}:{}'.format(self.hostname, agg['checksum']),
                        #                 "full_data": agg,
                        #                 "deleted": False,
                        #             }
                        #         })
                        datestamps = out.pop('datestamp')
                        if datestamps:
                            try:
                                out['datestamp'] = datetime.fromisoformat(datestamps[0]).astimezone(timezone.utc)
                            except ValueError:
                                pass

                        self.records.append(out)
        return self.records

if __name__ == "__main__":
    from harvest import extract_fields
    max_id = sys.argv[2] if len(sys.argv) > 2 else 2000
    force = True if len(sys.argv) > 3 and sys.argv[3] else False
    indexer = SpipIndexer(sys.argv[1], max_id=max_id)
    for rec in indexer.harvest(force=force):
        pp.pprint(rec)
        pp.pprint(extract_fields(rec, urlparse(sys.argv[1]).hostname))
