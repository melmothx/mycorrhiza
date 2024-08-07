from lxml import etree
import os
import sys

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
    dublin_core = {}
    for tag in tags:
        values = []
        for dc in metadata.findall('{http://purl.org/dc/elements/1.1/}' + tag):
            values.append(dc.text)
        dublin_core[tag] = values
    return dublin_core

def scan_tree(tree):
    print(tree)
    for root, dirs, files in os.walk(tree):
        for hidden in [ d for d in dirs if d.startswith('.') ]:
            print("Removing {}".format(hidden))
            dirs.remove(hidden)

        print(root)
        print(dirs)
        print(files)

if __name__ == "__main__":
    scan_tree(sys.argv[1])
    
