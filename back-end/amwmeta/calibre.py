from lxml import etree
import os
import sys
import pprint

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
            print(tag + ' ' + str(dc.attrib))
            if tag == 'identifier':
                scheme = dc.attrib.get('{http://www.idpf.org/2007/opf}scheme')
                if scheme and scheme.lower() == 'isbn':
                    out['isbn'] = [ dc.text ]
                    continue
            values.append(dc.text)
        out[tag] = values
    return out

def scan_calibre_tree(tree):
    records = []
    for root, dirs, files in os.walk(tree):
        for hidden in [ d for d in dirs if d.startswith('.') ]:
            # print("Removing {}".format(hidden))
            dirs.remove(hidden)
        if 'metadata.opf' in files:
            metadata = parse_opf(os.path.join(root, 'metadata.opf'))
            metadata['uri'] = [ root ]
            if metadata.get('identifier'):
                records.append(metadata)
    return records;

if __name__ == "__main__":
    pp.pprint(scan_calibre_tree(sys.argv[1]))
    
