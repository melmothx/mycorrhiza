from sickle import Sickle
from sickle.oaiexceptions import *
import logging
from sickle.models import Record
import re
import hashlib


logger = logging.getLogger(__name__)

class MarcXMLRecord(Record):
    def get_metadata(self):
        ns = { None: 'http://www.loc.gov/MARC21/slim' }
        specs = [
            # for now consider 720a the authors, including contributors
            # ('contributor', '720',  'a'),
            ('national_bibliography_number', '015',  ('a')),
            ('isbn', '020',  ('a')),
            ('terms_of_availability', '020',  ('c')),
            ('issn', '022',  ('a')),
            ('wrong_issn', '022',  ('y')),
            ('identifier', '024',  ('a')),
            ('language', '041', ('a')),
            ('country_of_publishing', '044',  ('c')),
            ('creator', '100', ('a')),
            ('agent_details', '100',  ('a', 'd', '4', 'e')),
            ('title_for_search', '222',  ('a')),
            ('title', '245',  ('a', 'b', 'c')),
            ('subtitle', '246',  ('a')),
            ('former_title', '247',  ('a', 'f')),
            ('edition_statement', '250',  ('a')),
            ('publisher', '260',  ('b')),
            ('publisher', '264',  ('b')),
            ('place_date_of_publication_distribution', '260', ('a', 'c')),
            ('place_date_of_publication_distribution', '264', ('a', 'c')), # this is actually the place + date
            ('physical_description', '300', ('a', 'b', 'c', 'e')),
            ('content_type', '336',  ('a')),
            ('date', '264', ('c')),
            ('date', '363', ('i')),
            ('date', '362', ('a')), # normalized date
            ('general_note', '500', ('a')),
            ('with_note', '501', ('a')),
            ('dissertation_note', '502', ('a')),
            ('numbering_peculiarities__note', '515', ('a')),
            ('description', '520',  ('a')),
            ('rights', '540',  ('a')),
            ('language', '546',  ('a')),
            ('issuing_body_note', '550', ('a')),
            ('cumulative_index_aids_note', '555', ('a')),
            ('added_entry_personal_name', '700',  ('a')),
            ('added_entry_relator_term', '700',  ('e')),
            ('supplement_relationship_information', '770',  ('a')),
            ('added_entry_title', '770',  ('t')),
            ('added_entry_place_publisher_date', '770',  ('d')),
            ('preceding_entry_relationship_information', '780',  ('i')),
            ('preceding_entry_title', '780',  ('t')),
            ('preceding_entry_place_publisher_date', '780',  ('d')),
            ('uri_info', '856', ('u', 'q', 'y')),
            ('uri', '856', ('u')),
            # https://wiki.koha-community.org/wiki/Holdings_data_fields_(9xx)
            ('koha_uri', '952', ('u')),
            ('shelf_location_code', '952', ('o')),
            ('serial_enumeration_caption', '952', ('h')),
            ('shelf_location_code', '852', ('c')),
            ('trade_price_value', '365', ('b')),
            ('trade_price_currency', '365', ('c')),
            ('subject', '653', ('a')),
        ]
        structured = {
            'uri_info': ('uri', 'content_type', 'label'),
            'agent_details': ('name', 'dates', 'relationship', 'relator_term'),
        }
        out = {}
        # expecting just one though
        for node in self.xml.findall('.//' + self._oai_namespace + 'metadata'):
            for spec in specs:
                target, tag, codes = spec
                if not target in out:
                    out[target] = []
                # https://docs.python.org/3/library/xml.etree.elementtree.html#elementtree-xpath

                for el in node.findall('.//datafield[@tag="{0}"]'.format(tag), namespaces=ns):
                    # here we're inside each tag.
                    values = []
                    composed = None
                    structured_data = {}
                    if target in structured:
                        composed = dict(zip(codes, structured[target]))

                    for code in codes:
                        # print("Searching " + code + " in " + tag)
                        for sf in el.findall('.//subfield[@code="{0}"]'.format(code), namespaces=ns):
                            values.append(sf.text)
                            if composed:
                                structured_data[composed[code]] = sf.text
                    # print(values)
                    if len(values):
                        if composed:
                            out[target].append(structured_data)
                        else:
                            out[target].append(' '.join(values))
        return out

def iso_lang_code(code):
    if not code:
        return None

    full_names = {
        "france": "fr",
        "francese": "fr",
        "inglese": "en",
        "italiano": "it",
        "spagnolo": "es",
        "tedesco": "de",
    }


    lang_code_re = re.compile(r'^[a-z]{2,3}$', re.IGNORECASE)
    match = lang_code_re.match(code)
    if match:
        actual_code = match.group().lower()
        mapping = {
            'abk': 'ab',
            'aar': 'aa',
            'afr': 'af',
            'aka': 'ak',
            'sqi': 'sq',
            'amh': 'am',
            'ara': 'ar',
            'arg': 'an',
            'hye': 'hy',
            'asm': 'as',
            'ava': 'av',
            'ave': 'ae',
            'aym': 'ay',
            'aze': 'az',
            'bam': 'bm',
            'bak': 'ba',
            'eus': 'eu',
            'bel': 'be',
            'ben': 'bn',
            'bis': 'bi',
            'bos': 'bs',
            'bre': 'br',
            'bul': 'bg',
            'mya': 'my',
            'cat': 'ca',
            'cha': 'ch',
            'che': 'ce',
            'nya': 'ny',
            'zho': 'zh',
            'chu': 'cu',
            'chv': 'cv',
            'cor': 'kw',
            'cos': 'co',
            'cre': 'cr',
            'hrv': 'hr',
            'ces': 'cs',
            'dan': 'da',
            'div': 'dv',
            'nld': 'nl',
            'dzo': 'dz',
            'eng': 'en',
            'epo': 'eo',
            'est': 'et',
            'ewe': 'ee',
            'fao': 'fo',
            'fij': 'fj',
            'fin': 'fi',
            'fra': 'fr',
            'fry': 'fy',
            'ful': 'ff',
            'gla': 'gd',
            'glg': 'gl',
            'lug': 'lg',
            'kat': 'ka',
            'deu': 'de',
            'ell': 'el',
            'kal': 'kl',
            'grn': 'gn',
            'guj': 'gu',
            'hat': 'ht',
            'hau': 'ha',
            'heb': 'he',
            'her': 'hz',
            'hin': 'hi',
            'hmo': 'ho',
            'hun': 'hu',
            'isl': 'is',
            'ido': 'io',
            'ibo': 'ig',
            'ind': 'id',
            'ina': 'ia',
            'ile': 'ie',
            'iku': 'iu',
            'ipk': 'ik',
            'gle': 'ga',
            'ita': 'it',
            'jpn': 'ja',
            'jav': 'jv',
            'kan': 'kn',
            'kau': 'kr',
            'kas': 'ks',
            'kaz': 'kk',
            'khm': 'km',
            'kik': 'ki',
            'kin': 'rw',
            'kir': 'ky',
            'kom': 'kv',
            'kon': 'kg',
            'kor': 'ko',
            'kua': 'kj',
            'kur': 'ku',
            'lao': 'lo',
            'lat': 'la',
            'lav': 'lv',
            'lim': 'li',
            'lin': 'ln',
            'lit': 'lt',
            'lub': 'lu',
            'ltz': 'lb',
            'mkd': 'mk',
            'mlg': 'mg',
            'msa': 'ms',
            'mal': 'ml',
            'mlt': 'mt',
            'glv': 'gv',
            'mri': 'mi',
            'mar': 'mr',
            'mah': 'mh',
            'mon': 'mn',
            'nau': 'na',
            'nav': 'nv',
            'nde': 'nd',
            'nbl': 'nr',
            'ndo': 'ng',
            'nep': 'ne',
            'nor': 'no',
            'nob': 'nb',
            'nno': 'nn',
            'iii': 'ii',
            'oci': 'oc',
            'oji': 'oj',
            'ori': 'or',
            'orm': 'om',
            'oss': 'os',
            'pli': 'pi',
            'pus': 'ps',
            'fas': 'fa',
            'pol': 'pl',
            'por': 'pt',
            'pan': 'pa',
            'que': 'qu',
            'ron': 'ro',
            'roh': 'rm',
            'run': 'rn',
            'rus': 'ru',
            'sme': 'se',
            'smo': 'sm',
            'sag': 'sg',
            'san': 'sa',
            'srd': 'sc',
            'srp': 'sr',
            'sna': 'sn',
            'snd': 'sd',
            'sin': 'si',
            'slk': 'sk',
            'slv': 'sl',
            'som': 'so',
            'sot': 'st',
            'spa': 'es',
            'sun': 'su',
            'swa': 'sw',
            'ssw': 'ss',
            'swe': 'sv',
            'tgl': 'tl',
            'tah': 'ty',
            'tgk': 'tg',
            'tam': 'ta',
            'tat': 'tt',
            'tel': 'te',
            'tha': 'th',
            'bod': 'bo',
            'tir': 'ti',
            'ton': 'to',
            'tso': 'ts',
            'tsn': 'tn',
            'tur': 'tr',
            'tuk': 'tk',
            'twi': 'tw',
            'uig': 'ug',
            'ukr': 'uk',
            'urd': 'ur',
            'uzb': 'uz',
            'ven': 've',
            'vie': 'vi',
            'vol': 'vo',
            'wln': 'wa',
            'cym': 'cy',
            'wol': 'wo',
            'xho': 'xh',
            'yid': 'yi',
            'yor': 'yo',
            'zha': 'za',
            'zul': 'zu',
        }
        return mapping.get(actual_code, actual_code)
    else:
        return full_names.get(code.lower())

def harvest_oai_pmh(url, opts):
    logger.debug([url, opts])
    if opts['metadataPrefix'] == 'marc21':
        sickle = Sickle(url, class_mapping={
            "ListRecords": MarcXMLRecord,
            "GetRecord": MarcXMLRecord,
        })
    else:
        sickle = Sickle(url)

    try:
        records = sickle.ListRecords(**opts)
    except NoRecordsMatch:
        return []

    # just return the iterator
    return records

def extract_fields(record, hostname):
    out = {}
    # here we map the full metadata to a subset for the DB. All the
    # fields are lists, so we either collapse them (default) or filter
    # somehow.

    # clean and sort the dates
    years = re.compile(r'[12][0-9]{3}')
    if "date" in record:
        all_dates = []
        for date in record['date']:
            all_dates.extend(years.findall(date))
        unique_dates = sorted(list(set(all_dates)))
        if unique_dates:
            if len(unique_dates) == 1:
                out['year_edition'] = unique_dates[0]
            else:
                out['year_edition'] = unique_dates[-1]
                out['year_first_edition'] = unique_dates[0]

    url_re = re.compile('https?://')
    if "uri_info" in record:
        # be sure that we have real urls
        uri_lists = [ u for u in record['uri_info'] if url_re.match(u.get('uri', '')) ]
        # here we have a bit of logic.
        # if there's only one record, no brainer.
        good_uri = None
        if len(uri_lists) == 1:
            good_uri = uri_lists[0]
        elif uri_lists:
            same_host = re.compile('https?://' + re.escape(hostname))
            same_host_uris = [ u for u in uri_lists if same_host.match(u['uri']) ]
            if same_host_uris:
                good_uri = same_host_uris[0]
            else:
                # give up, use the first one
                good_uri = uri_lists[0]

        if good_uri:
            out['uri'] = good_uri['uri']
            out['content_type'] = good_uri.get('content_type', '')
            out['uri_label'] = good_uri.get('label', '')

    if not out.get('uri'):
        try:
            out['uri'] = record['koha_uri'][0]
        except IndexError:
            pass
        except KeyError:
            pass

    if record.get('shelf_location_code'):
        out['shelf_location_code'] = ' / '.join(record.get('shelf_location_code'))

    if record.get('physical_description'):
        out['material_description'] = ' '.join(record.get('physical_description'))

    mapping = {
        "title": {
            "checksum": True,
        },
        "creator": {
            "list": "authors",
            "checksum": True,
        },
        "language": {
            "list": "languages",
            "checksum": True,
            "interpolate": iso_lang_code,
        },
        "subtitle": {
            "checksum": True,
        },
        "description": {},
    }
    sha = hashlib.sha256()
    for field in sorted(mapping):
        spec = mapping[field]
        checksum = spec.get('checksum', False)
        outfield = field
        values = record.get(field, [])
        interpolate = spec.get('interpolate')
        if values and interpolate:
            cleaned_values = []
            for v in values:
                cv = interpolate(v)
                if cv:
                    cleaned_values.append(cv)
            values = cleaned_values

        if "list" in spec:
            outfield = spec['list']
            out[outfield] = values
            if checksum:
                for f in out[outfield]:
                    # logger.debug("adding " + f)
                    sha.update(f.encode())
        else:
            # collapse
            words = re.compile(r"\w")
            out[outfield] = ' '.join([ s for s in values if words.search(s)])
            if checksum:
                # logger.debug("adding " + out[field])
                sha.update(out[outfield].encode())

    out['checksum'] = sha.hexdigest()
    return out

