import requests
import json
from datetime import datetime
from pathlib import Path
import logging
import pprint
import re
import urllib.parse

pp = pprint.PrettyPrinter(indent=2)
logger = logging.getLogger(__name__)


class WikidataRetriever:
    def __init__(self,
                 access_token=None,
                 endpoint="https://www.wikidata.org/w/rest.php/wikibase",
                 language="en",
                 cache_dir="wikidatacache",
                 cache_expire=7,
                 ):
        self.access_token = access_token
        self.endpoint = endpoint
        self.cache_dir = cache_dir
        self.cache_expire = cache_expire * 3600 * 24
        self.language = language
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mycorrhiza/1.0 (https://github.com/melmothx/mycorrhiza)",
            "Authorization": "Bearer {}".format(self.access_token)
        }
    def retrieve(self, path):
        cache = Path(self.cache_dir + path)
        # print("Cache is {} {}".format(self.cache_dir, cache))
        if cache.exists():
            rcache = json.loads(cache.read_text(encoding='UTF-8'))
            if datetime.now().timestamp() - rcache['ts'] < self.cache_expire:
                return rcache['data']
        r = requests.get(self.endpoint + path, headers=self.headers)
        r.raise_for_status()
        data = r.json()
        wcache = {
            "ts": datetime.now().timestamp(),
            "data": data,
        }
        cache.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Writing cache to {}".format(cache))
        cache.write_text(json.dumps(wcache, ensure_ascii=False, sort_keys=True, indent=2), encoding='UTF-8')
        return data
    def get_property(self, pid):
        return self.retrieve('/v1/entities/properties/{}'.format(pid))
    def get_item(self, item):
        return self.retrieve('/v1/entities/items/{}'.format(item))
    def show_item(self, item):
        lang = self.language
        out = {}
        data = self.get_item(item)
        labels = data.get('labels')
        if labels:
            out['name'] = labels.get(lang) or labels.get('en')
        descriptions = data.get('descriptions')
        if descriptions:
            out['desc'] = descriptions.get(lang) or descriptions.get('en')
        try:
            out['link'] = data['sitelinks'][lang + 'wiki']['url']
        except KeyError:
            try:
                out['link'] = data['sitelinks']['enwiki']['url']
            except KeyError:
                pass
        out['statements'] = []
        statements = data.get('statements')

        supported = (
            # image
            'P18',
            # signature
            'P109',
            # name in native language
            'P1559',
            # logo image
            'P154',
            # title
            'P1476',
            # official website
            'P856',
            # headquarters location
            'P159',
            # given name
            'P735',
            # patronym oir matronym
            'P5056',
            # family name
            'P734',
            # notable works
            'P800',
            # country of origin
            'P495',
            # place of birth
            'P19',
            # date of birth
            'P569',
            # inception - magazines
            'P571',
            # pubblication date
            'P577',
            # place fo death
            'P20',
            # date fo death
            'P570',
            # manner of death
            'P1196',
            # cause of death
            'P509',
            # date of official closure
            'P3999',
            # dissolved, abolished
            'P576',
            # viaf
            'P214',
            # archives at
            'P485',
            # founded by
            'P112',
            # language of work or name
            'P407',
            # language spoken written or signed
            'P1412',
            # Library of congress authority
            # 'P244',
            # mother
            # 'P25',
            # father
            # 'P26',
        )
        if statements:
            for prop in supported:
                plables = self.get_property(prop).get('labels', {})
                label = plables.get(lang) or plables.get('en')
                if label:
                    contents = []
                    for p in statements.get(prop, []):
                        value, data_type = self.get_property_value(p)
                        if value:
                            contents.append(value)
                    if contents:
                        out['statements'].append({
                            "name": label,
                            "values": contents,
                            "property": prop,
                            "data_type": data_type,
                        })
        return out
    def get_property_value(self, prop):
        data_type = prop['property']['data_type']
        wikipid = prop['property']['id']
        if data_type == 'time':
            precision = prop['value']['content']['precision']
            date = None
            rawdate = prop['value']['content']['time']
            if rawdate.startswith('+') and precision >= 11:
                rawdate = rawdate[1:]
                date = re.sub(r'T.*$', '', rawdate)
            else:
                m = re.match('^([+-])?([0-9]{4})', rawdate)
                if m:
                    if m.group(1) == '-':
                        date = "{}{}".format(m.group(1), m.group(2))
                    else:
                        date = m.group(2)
            return (date, data_type)
        elif data_type == 'wikibase-item':
            item = self.get_item(prop['value']['content'])
            labels = item.get('labels')
            if labels:
                value = labels.get(self.language) or labels.get('en')
                if value:
                    return (value, data_type)
                else:
                    return (None, data_type)
        elif data_type == 'external-id':
            value = prop['value']['content']
            if value and wikipid == 'P214':
                value = "https://viaf.org/viaf/{}".format(value)
            return (value, data_type)
        elif data_type == 'commonsMedia':
            value = prop['value']['content']
            if value.startswith('File:'):
                value = value[5:]
            value = value.replace(' ', '_')
            value = "https://commons.wikimedia.org/w/thumb.php?width=300&f={}".format(urllib.parse.quote(value))
            return (value, data_type)
        elif data_type == 'monolingualtext':
            value = prop['value']['content']['text']
            return (value, data_type)
        try:
            v = prop['value']['content']
        except KeyError:
            pass
        return (v, data_type)
