from lxml import etree

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
    
