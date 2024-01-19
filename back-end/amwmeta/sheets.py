import csv
import logging
import re
logger = logging.getLogger(__name__)


def parse_sheet(csv_type, sheet, **options):
    args = {
        "calibre": {
            "encoding": "utf-8-sig",
            "csv": {
                "delimiter": ",",
                "doublequote": True,
            },
        },
        "abebooks_home_base": {
            "encoding": "latin-1",
            "csv": {
                "delimiter": ",",
                "doublequote": True,
            },
        }
    }
    with open(sheet, newline='', encoding=args[csv_type]['encoding']) as csvfile:
        reader = csv.DictReader(csvfile, **args[csv_type]['csv'])
        out = []
        for row in reader:
            if options.get('sample'):
                logger.debug(row)
                return row
            out.append(row)
        return out

def normalize_records(csv_type, records):
    mappings = {
        "calibre": [
            ('title', 'title', None),
            ('date', 'pubdate', None),
            ('publisher', 'publisher', None),
            ('description', 'comments', None),
            ('isbn', 'isbn', None),
            ('language', 'languages', re.compile(r'\s*,\s*')),
            ('creator', 'authors', re.compile(r'\s*&\s*')),
            ('subject', 'tags', re.compile(r'\s*,\s*')),
            ('identifier', 'uuid', None),
            ('identifier', 'id', None),
        ],
        "abebooks_home_base": [
            ('title', 'Title', None),
            ('date', 'Publisher Year', None),
            ('publisher', 'publisher', None),
            ('description', 'Description', None),
            ('description', 'Synopsis', None),
            ('place_date_of_publication_distribution', 'Publisher Place', None),
            ('isbn', 'Isbn', None),
            ('language', 'Language', re.compile(r'\s*,\s*')),
            ('creator', 'Author', re.compile(r'\s*/\s*')),
            ('subject', 'Keywords', None),
            ('identifier', 'Book ID', None),
        ]

    }
    # let it crash with missing type
    out = []
    for rec in records:
        normal = {}
        for spec in mappings[csv_type]:
            dest, orig, split = spec
            if not dest in normal:
                normal[dest] = []

            value = rec.get(orig)
            if value:
                if split:
                    normal[dest].extend(split.split(value))
                else:
                    normal[dest].append(value)
        out.append(normal)
    return out
