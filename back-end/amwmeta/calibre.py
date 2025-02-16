from lxml import etree
import os
import sys
import pprint
from pathlib import Path
from datetime import datetime, timezone

pp = pprint.PrettyPrinter(indent=2)


def parse_opf(opf_file):
    doc = etree.parse(opf_file)
    metadata = doc.getroot().find('{http://www.idpf.org/2007/opf}metadata')
    tags = [
        'identifier',
        'title',
        'date',
        'publisher',
        'language',
        'description',
        'creator',
        'subject',
    ]
    out = {}
    for tag in tags:
        values = []
        for dc in metadata.findall('{http://purl.org/dc/elements/1.1/}' + tag):
            if tag == 'identifier':
                scheme = dc.attrib.get('{http://www.idpf.org/2007/opf}scheme')
                if scheme and scheme.lower() == 'isbn':
                    out['isbn'] = [ dc.text ]
                    continue
            values.append(dc.text)
        out[tag] = values

        # in a calibre tree we are probably going to find a single issue, not articles.
        # our implementation for the aggregations is relative to single articles.
        # So either we aggregate by "series" or don't aggreegate at all.
        # aggregation = {}
        # for meta in metadata.findall('{http://www.idpf.org/2007/opf}meta'):
        #     if meta.attrib.get('name') == 'calibre:series':
        #         aggregation['name'] = meta.attrib.get('content')
        #     # we don't expect to find articles here, just whole issues
        #     # if meta.attrib.get('name') == 'calibre:series_index':
        #     #    aggregation['issue'] = meta.attrib.get('content')
        # if 'name' in aggregation:
        #     out['aggregation'] = [ aggregation ]
    return out

def scan_calibre_tree(tree, since=None):
    records = []
    since_epoch = 0
    if since:
        since_epoch = since.timestamp()
    # print("Reference time is {}".format(since_epoch))
    # print("Calling scan_calibre_tree against " + tree)
    for root, dirs, files in os.walk(tree):
        for hidden in [ d for d in dirs if d.startswith('.') ]:
            # print("Removing {}".format(hidden))
            dirs.remove(hidden)
        if 'metadata.opf' in files:
            metadata_file = os.path.join(root, 'metadata.opf')
            file_epoch = Path(metadata_file).stat().st_mtime
            datestamp = datetime.fromtimestamp(file_epoch, tz=timezone.utc)
            if since_epoch:
                if file_epoch < since_epoch:
                    continue
            metadata = parse_opf(metadata_file)
            metadata['file_uri'] = [ root ]
            metadata['datestamp'] = datestamp
            if metadata.get('identifier'):
                records.append(metadata)
    return records;

if __name__ == "__main__":
    # scan_calibre_tree(sys.argv[1])
    since = None
    try:
        if sys.argv[2]:
            since = datetime.fromisoformat(sys.argv[2])
    except IndexError:
        pass
    for rec in scan_calibre_tree(sys.argv[1], since=since):
        pp.pprint(rec)
        print("{}".format(rec['datestamp']))
    
