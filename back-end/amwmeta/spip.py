import requests
from lxml import html,etree
import logging
import pprint
import sys
import re
import hashlib
from urllib.parse import urlparse, urljoin
from datetime import datetime,timezone

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=2)

def extract_text_from_element(el, url):
    BLOCK_TAGS = {"div", "p", "hr", "pre", "li", "br"}
    parts = []
    def walk(node):
        if node.text:
            parts.append(re.sub(r'\s+', ' ', node.text))
        if node.tag == 'a' or node.tag == '<img>':
            link = node.get('href') or node.get('src')
            if link:
                u = urljoin(url, link)
                if node.text and u in node.text:
                    pass
                else:
                    parts.append(" [{}] ".format(u))
        for child in node:
            if child.tag in BLOCK_TAGS:
                if parts and parts[-1] == "\n":
                    pass
                else:
                    parts.append("\n")
            walk(child)
        if node.tail:
            parts.append(re.sub(r'\s+', ' ', node.tail))
    walk(el)
    return {
        "body": "".join(parts),
    }

class SpipIndexer:
    def __init__(self, base_url, max_id=2000, skip_fields=[], body_is_description=True):
        self.max_id = max_id
        self.base_url = base_url
        self.hostname = urlparse(base_url).hostname
        self.skip_fields = skip_fields
        self.body_is_description = body_is_description
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
            ('dc.relation', 'aggregation'),
        ]
        for url in urls:
            good = re.fullmatch(r'.*/article([0-9]+)\.html', url)
            if good:
                identifier = good.group(1)
                r = self.ua.get(url)
                if r.status_code == 200:
                    r.encoding = 'utf-8'
                    doc = html.fromstring(r.text)
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
                        if tagname in self.skip_fields:
                            continue
                        if dest not in out:
                            out[dest] = []
                        for el in doc.xpath("//meta[@name='{}']".format(tagname)):
                            text = el.attrib.get('content')
                            if text:
                                out[dest].append(text)
                    if out['title']:
                        if out.get('aggregation'):
                            out['aggregation'] = [ { "name": agg } for agg in out['aggregation'] ]
                            if out['aggregation']:
                                out['aggregation_objects'] = []
                                for agg in out['aggregation']:
                                    asha = hashlib.sha256()
                                    asha.update(agg['name'].encode())
                                    agg['checksum'] = asha.hexdigest()
                                    out['aggregation_objects'].append({
                                        'order': None,
                                        'data': {
                                            'title': agg['name'],
                                            "checksum": agg['checksum'],
                                            'identifier': 'aggregation:{}:{}'.format(self.hostname, agg['checksum']),
                                            "full_data": agg,
                                            "deleted": False,
                                        }
                                    })
                        if self.body_is_description:
                            xpath = "//*[contains(concat(' ', normalize-space(@class), ' '), ' {}-{} ')]"
                            full_body = []
                            for spip_class in ('article-chapo', 'article-texte', 'article-descriptif', 'article-ps'):
                                for el in doc.xpath(xpath.format(spip_class, identifier)):
                                    fragment = extract_text_from_element(el, url)
                                    if fragment['body']:
                                        full_body.append(fragment['body'])
                                        if spip_class == 'article-chapo':
                                            m = re.match(r'.*([0-9]{4})', fragment['body'])
                                            if m:
                                                possible_date = m.group(1)
                                                if int(possible_date) > 1800 and int(possible_date) < 2050:
                                                    out['date'] = [ possible_date ]
                            if full_body:
                                out.setdefault('description', []).append("".join(full_body))
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
    skip_fields = [ f for f in re.split(r'[^a-zA-Z0-9.]', sys.argv[4]) if f ] if len(sys.argv) > 4 and sys.argv[4] else []
    indexer = SpipIndexer(sys.argv[1], max_id=max_id, skip_fields=skip_fields)
    for rec in indexer.harvest(force=force):
        pp.pprint(rec)
        pp.pprint(extract_fields(rec, urlparse(sys.argv[1]).hostname))
