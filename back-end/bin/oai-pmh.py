#!/usr/bin/env python3
from sickle import Sickle
from sickle.models import Record
import xml.dom.minidom
import pprint
import sys
sys.path.append('.')
from amwmeta.harvest import UniMarcXMLRecord, MarcXMLRecord, extract_fields
import argparse
from urllib.parse import urlparse
parser = argparse.ArgumentParser()
parser.add_argument("endpoint", help="OAI-PMH endpoint URL")
parser.add_argument("--identifier", help="OAI-PMH identifier")
parser.add_argument("--unimarc", action="store_true")
args = parser.parse_args()

mapping = {
    "ListRecords": MarcXMLRecord,
    "GetRecord": MarcXMLRecord,
}

if args.unimarc:
    mapping = {
        "ListRecords": UniMarcXMLRecord,
        "GetRecord": UniMarcXMLRecord,
    }

pp = pprint.PrettyPrinter(compact=True)
sickle = Sickle(args.endpoint, class_mapping=mapping);

if args.identifier:
    rec = sickle.GetRecord(metadataPrefix="marc21",
                           identifier=args.identifier)
    dom = xml.dom.minidom.parseString(rec.raw)
    print(dom.toprettyxml(indent="  "))
    data = rec.get_metadata();
    pp.pprint(data)
    pp.pprint(extract_fields(data, urlparse(args.endpoint).hostname))
    pp.pprint(rec.header)

else:
    records = sickle.ListRecords(metadataPrefix="marc21")
    for rec in records:
        try:
            print(rec.header.identifier)
        except:
            pass

