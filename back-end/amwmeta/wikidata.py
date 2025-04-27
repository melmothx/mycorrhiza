import requests
import json
from datetime import datetime
from pathlib import Path
import logging
import pprint

pp = pprint.PrettyPrinter(indent=2)
logger = logging.getLogger(__name__)


class WikidataRetriever:
    def __init__(self,
                 access_token=None,
                 endpoint="https://www.wikidata.org/w/rest.php/wikibase",
                 cache_dir="wikidatacache",
                 cache_expire=7
                 ):
        self.access_token = access_token
        self.endpoint = endpoint
        self.cache_dir = cache_dir
        self.cache_expire = cache_expire * 3600 * 24
        self.headers = {
            "Content-Type": "application/json",
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
    def show_item(self, item, lang='en'):
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
        if statements:
            for prop in statements:
                plables = self.get_property(prop).get('labels', {})
                label = plables.get(lang) or plables.get('en')
                if label:
                    contents = []
                    for p in statements[prop]:
                        try:
                            v = p['value']['content']
                            if v:
                                contents.append(v)
                        except KeyError:
                            pass
                    out['statements'].append({
                        "name": label,
                        "values": contents,
                        "property": prop,
                    })
        return out
