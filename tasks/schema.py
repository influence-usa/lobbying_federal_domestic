import logging
from datetime import datetime
import locale

from .log import set_up_logging

log = set_up_logging('schema', loglevel=logging.DEBUG)

REPLACE_MAP = {u'&#160;': u'',
               u'\xa0':  u'',
               u'&nbsp;': u''}

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def checkbox_boolean(e):
    return 'checked' in e.attrib


def clean_text(e):
    s = e.text or ''
    s = s.strip()
    for p, r in REPLACE_MAP.iteritems():
        s = s.replace(p, r)
    return s


def parse_datetime(e):
    s = clean_text(e)
    if s:
        try:
            return datetime.strptime(s, '%m/%d/%Y').isoformat()
        except ValueError:
            return datetime.strptime(s, '%m/%d/%Y %I:%M:%S %p').isoformat()
    else:
        return None


def tail_text(e):
    s = e.tail
    for p, r in REPLACE_MAP.iteritems():
        s = s.replace(p, r)
    return s.strip()


def parse_decimal(e):
    s = clean_text(e)
    if s:
        return locale.atof(s)
    else:
        return None


def parse_int(e):
    s = clean_text(e)
    if s:
        return int(s)
    else:
        return None


def parse_percent(e):
    s = clean_text(e).replace('%', '')
    if s:
        return float(s) / 100.0
    else:
        return None


def split_keep_rightmost(e):
    s = clean_text(e)
    split_text = s.split(' ')
    if len(split_text) > 1:
        return split_text[-1]
    else:
        return None


def parse_array(array, children):
    for element in array:
        record = {}
        for child in children:
            _parser = child['parser']
            _field = child['field']
            _path = child['path']
            _child_node = element.xpath(_path)[0]
            if child.get('children', False):
                record[_field] = _parser(_child_node, child['children'])
            else:
                record[_field] = _parser(_child_node)
        yield record


def parse_even_odd(array, children):
    for even, odd in zip([(array[i], array[i+1])
                          for i in xrange(0, len(array), 2)]):
        record = {}
        for element in even:
            for child in children['even']:
                _parser = child['parser']
                _field = child['field']
                _path = child['path']
                _child_node = element.xpath(_path)
                record[_field] = _parser(_child_node)
        for element in odd:
            for child in children['odd']:
                _parser = child['parser']
                _field = child['field']
                _path = child['path']
                _child_node = element.xpath(_path)
                record[_field] = _parser(_child_node)
        yield record


ld1_schema = [
    {
        'section': 'registration_type',
        'lda_question': None,
        'field': 'new_registrant',
        'path': '/html/body/div[1]/input[1]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registration_type',
        'lda_question': None,
        'field': 'new_client_for_existing_registrant',
        'path': '/html/body/div[1]/input[2]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registration_type',
        'lda_question': None,
        'field': 'amendment',
        'path': '/html/body/div[1]/input[3]',
        'parser': checkbox_boolean
    },
    {
        'section': 'datetimes',
        'lda_question': '1',
        'field': 'effective_date',
        'path': '/html/body/table[2]/tbody/tr[1]/td[3]/div',
        'parser': parse_datetime
    },
    {
        'section': 'identifiers',
        'lda_question': '2',
        'field': 'registrant_house_id',
        'path': '/html/body/table[2]/tbody/tr[2]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'identifiers',
        'lda_question': '2',
        'field': 'registrant_senate_id',
        'path': '/html/body/table[2]/tbody/tr[2]/td[5]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': None,
        'field': 'organization_or_lobbying_firm',
        'path': '/html/body/p[3]/input[1]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registrant',
        'lda_question': None,
        'field': 'self_employed_individual',
        'path': '/html/body/p[3]/input[2]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_name',
        'path': '/html/body/table[3]/tbody/tr/td[3]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_address_one',
        'path': '/html/body/table[4]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_address_two',
        'path': '/html/body/table[4]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_city',
        'path': '/html/body/table[5]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_state',
        'path': '/html/body/table[5]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_zip',
        'path': '/html/body/table[5]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_country',
        'path': '/html/body/table[5]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4',
        'field': 'registrant_ppb_city',
        'path': '/html/body/table[6]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4',
        'field': 'registrant_ppb_state',
        'path': '/html/body/table[6]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4',
        'field': 'registrant_ppb_zip',
        'path': '/html/body/table[6]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4',
        'field': 'registrant_ppb_country',
        'path': '/html/body/table[6]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '5',
        'field': 'registrant_international_phone',
        'path': '/html/body/table[7]/tbody/tr/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'registrant',
        'lda_question': '5',
        'field': 'registrant_contact',
        'path': '/html/body/table[8]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '5',
        'field': 'registrant_phone',
        'path': '/html/body/table[8]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '5',
        'field': 'registrant_email',
        'path': '/html/body/table[8]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '5',
        'field': 'registrant_email',
        'path': '/html/body/table[8]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '6',
        'field': 'registrant_general_description',
        'path': '/html/body/div[2]',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': None,
        'field': 'client_self',
        'path': '/html/body/p[4]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_name',
        'path': '/html/body/table[9]/tbody/tr[1]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_address',
        'path': '/html/body/table[9]/tbody/tr[2]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_city',
        'path': '/html/body/table[10]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_state',
        'path': '/html/body/table[10]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_zip',
        'path': '/html/body/table[10]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_country',
        'path': '/html/body/table[10]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '8',
        'field': 'client_ppb_city',
        'path': '/html/body/table[11]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '8',
        'field': 'client_ppb_state',
        'path': '/html/body/table[11]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '8',
        'field': 'client_ppb_zip',
        'path': '/html/body/table[11]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '8',
        'field': 'client_ppb_country',
        'path': '/html/body/table[11]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '9',
        'field': 'client_general_description',
        'path': '/html/body/div[3]',
        'parser': clean_text
    },
    {
        'section': 'lobbyists',
        'lda_question': '10',
        'field': 'lobbyists',
        'path': '/html/body/table[12]/tbody/tr[position() > 2]',
        'parser': parse_array,
        'children': [
            {
                'section': 'lobbyists',
                'lda_question': '10',
                'field': 'lobbyist_first_name',
                'path': 'td[1]',
                'parser': clean_text
            },
            {
                'section': 'lobbyists',
                'lda_question': '10',
                'field': 'lobbyist_last_name',
                'path': 'td[2]',
                'parser': clean_text
            },
            {
                'section': 'lobbyists',
                'lda_question': '10',
                'field': 'lobbyist_suffix',
                'path': 'td[3]',
                'parser': clean_text
            },
            {
                'section': 'lobbyists',
                'lda_question': '10',
                'field': 'lobbyist_covered_official_position',
                'path': 'td[4]',
                'parser': clean_text
            },
        ]
    },
    {
        'section': 'lobbying_issues',
        'lda_question': '11',
        'field': 'lobbying_issues',
        'path': '/html/body/table[13]/tbody/tr/td/div',
        'parser': parse_array,
        'children': [
            {
                'section': 'lobbying_issues',
                'lda_question': '11',
                'field': 'issue_code',
                'path': '.',
                'parser': clean_text
            },
        ]
    },
    {
        'section': 'lobbying_issues_detail',
        'lda_question': '12',
        'field': 'lobbying_issues_detail',
        'path': '/html/body/p[10]',
        'parser': clean_text
    },
    {
        'section': 'affiliated_organizations',
        'lda_question': '13',
        'field': 'affiliated_organizations_no',
        'path': '/html/body/table[14]/tbody/tr/td[1]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'affiliated_organizations',
        'lda_question': '13',
        'field': 'affiliated_organizations_yes',
        'path': '/html/body/table[14]/tbody/tr/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'affiliated_organizations',
        'lda_question': '13',
        'field': 'affiliated_organizations_url',
        'path': '/html/body/table[15]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'affiliated_organizations',
        'lda_question': '13',
        'field': 'affiliated_organizations',
        'path': '/html/body/table[16]/tbody/tr[position() > 3]',
        'parser': parse_even_odd,
        'children':
            {
                'odd': [
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_name',
                        'path': 'td[1]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_address',
                        'path': 'td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_ppb_city',
                        'path': 'td[3]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                ],
                'even': [
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_city',
                        'path': 'td[2]/table/tbody/tr/td[1]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_state',
                        'path': 'td[2]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_zip',
                        'path': 'td[2]/table/tbody/tr/td[3]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_country',
                        'path': 'td[2]/table/tbody/tr/td[4]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_ppb_state',
                        'path': 'td[3]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'affiliated_organizations',
                        'lda_question': '13',
                        'field': 'affiliated_organization_ppb_country',
                        'path': 'td[3]/table/tbody/tr/td[4]/div',
                        'parser': clean_text
                    },
                ]
            }
    },
    {
        'section': 'foreign_entities',
        'lda_question': '14',
        'field': 'foreign_entities_no',
        'path': '/html/body/table[17]/tbody/tr/td[1]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'foreign_entities',
        'lda_question': '14',
        'field': 'foreign_entities_yes',
        'path': '/html/body/table[17]/tbody/tr/td[3]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'foreign_entities',
        'lda_question': '14',
        'field': 'foreign_entities',
        'path': '/html/body/table[19]/tbody/tr',
        'parser': parse_even_odd,
        'children':
            {
                'odd': [
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_address',
                        'path': 'td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_city',
                        'path': 'td[3]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                ],
                'even': [
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_name',
                        'path': 'td[1]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_city',
                        'path': 'td[2]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_state',
                        'path': 'td[2]/table/tbody/tr/td[3]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_country',
                        'path': 'td[2]/table/tbody/tr/td[4]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_ppb_state',
                        'path': 'td[3]/table/tbody/tr/td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_ppb_country',
                        'path': 'td[3]/table/tbody/tr/td[4]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_amount',
                        'path': 'td[4]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'foreign_entities',
                        'lda_question': '14',
                        'field': 'foreign_entity_ownership_percentage',
                        'path': 'td[5]/div',
                        'parser': clean_text
                    }
                ]
            }
    },
    {
        'section': 'signature',
        'lda_question': None,
        'field': 'signature',
        'path': '/html/body/table[20]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'datetimes',
        'lda_question': None,
        'field': 'signature_date',
        'path': '/html/body/table[20]/tbody/tr/td[4]/div',
        'parser': parse_datetime
    }
]

ld2_schema = [
    {
        'section': 'registrant',
        'lda_question': '1',
        'field': 'organization_lobbying_firm',
        'path': '/html/body/div[1]/input[1]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registrant',
        'lda_question': '1',
        'field': 'self_employed_individual',
        'path': '/html/body/div[1]/input[2]',
        'parser': checkbox_boolean
    },
    {
        'section': 'registrant',
        'lda_question': '1',
        'field': 'registrant_name',
        'path': '/html/body/div[1]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_address_one',
        'path': '/html/body/div[1]/table[1]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_address_two',
        'path': '/html/body/div[1]/table[1]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_city',
        'path': '/html/body/div[1]/table[2]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_state',
        'path': '/html/body/div[1]/table[2]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_zip',
        'path': '/html/body/div[1]/table[2]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '2',
        'field': 'registrant_country',
        'path': '/html/body/div[1]/table[2]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_ppb_city',
        'path': '/html/body/div[1]/table[2]/tbody/tr/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_ppb_state',
        'path': '/html/body/div[1]/table[3]/tbody/tr/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '3',
        'field': 'registrant_ppb_zip',
        'path': '/html/body/div[1]/table[3]/tbody/tr/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4a',
        'field': 'registrant_contact_name_prefix',
        'path': '/html/body/div[1]/table[4]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[1]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4a',
        'field': 'registrant_contact_name',
        'path': '/html/body/div[1]/table[4]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4b',
        'field': 'registrant_contact_phone',
        'path': '/html/body/div[1]/table[4]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[3]/div',
        'parser': clean_text
    },
    {
        'section': 'registrant',
        'lda_question': '4c',
        'field': 'registrant_contact_email',
        'path': '/html/body/div[1]/table[4]/tbody/tr[1]/td[1]/table/tbody/tr[2]/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'identifiers',
        'lda_question': '5',
        'field': 'client_registrant_senate_id',
        'path': '/html/body/div[1]/table[4]/tbody/tr[1]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'identifiers',
        'lda_question': '6',
        'field': 'client_registrant_house_id',
        'path': '/html/body/div[1]/table[4]/tbody/tr[2]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_self',
        'path': '/html/body/div[1]/table[4]/tbody/tr[2]/td[1]/table/tbody/tr[1]/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_state_or_local_government',
        'path': '/html/body/div[1]/table[4]/tbody/tr[2]/td[1]/table/tbody/tr[1]/td[3]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'client',
        'lda_question': '7',
        'field': 'client_name',
        'path': '/html/body/div[1]/table[4]/tbody/tr[2]/td[1]/table/tbody/tr[2]/td/div',
        'parser': clean_text
    },
    {
        'section': 'report',
        'lda_question': '8',
        'field': 'report_year',
        'path': '/html/body/table[2]/tbody/td[3]/div',
        'parser': clean_text
    },
    {
        'section': 'report',
        'lda_question': '8',
        'field': 'report_quarter_one',
        'path': '/html/body/table[2]/tbody/td[4]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '8',
        'field': 'report_quarter_two',
        'path': '/html/body/table[2]/tbody/td[5]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '8',
        'field': 'report_quarter_three',
        'path': '/html/body/table[2]/tbody/td[6]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '8',
        'field': 'report_quarter_four',
        'path': '/html/body/table[2]/tbody/td[7]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '9',
        'field': 'report_is_amendment',
        'path': '/html/body/p[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '10',
        'field': 'report_is_termination',
        'path': '/html/body/table[3]/tbody/td[1]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'report',
        'lda_question': '10',
        'field': 'report_termination_date',
        'path': '/html/body/table[3]/tbody/td[3]/div',
        'parser': parse_datetime 
    },
    {
        'section': 'report',
        'lda_question': '11',
        'field': 'report_no_activity',
        'path': '/html/body/table[3]/tbody/td[4]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'income',
        'lda_question': '12',
        'field': 'income_less_than_five_thousand',
        'path': '/html/body/table[4]/tbody/tr[4]/td[1]/table/tbody/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'income',
        'lda_question': '12',
        'field': 'income_five_thousand_or_more',
        'path': '/html/body/table[4]/tbody/tr[5]/td[1]/table/tbody/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'income',
        'lda_question': '12',
        'field': 'income_amount',
        'path': '/html/body/table[4]/tbody/tr[5]/td[1]/table/tbody/td[4]/div',
        'parser': parse_decimal
    },
    {
        'section': 'expenses',
        'lda_question': '13',
        'field': 'expense_less_than_five_thousand',
        'path': '/html/body/table[4]/tbody/tr[4]/td[2]/table/tbody/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'expenses',
        'lda_question': '13',
        'field': 'expense_five_thousand_or_more',
        'path': '/html/body/table[4]/tbody/tr[5]/td[2]/table/tbody/td[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'expenses',
        'lda_question': '13',
        'field': 'expense_amount',
        'path': '/html/body/table[4]/tbody/tr[5]/td[2]/table/tbody/td[4]/div',
        'parser': parse_decimal
    },
    {
        'section': 'expenses',
        'lda_question': '14',
        'field': 'expense_method_a',
        'path': '/html/body/table[4]/tbody/tr[7]/td[2]/input',
        'parser': checkbox_boolean 
    },
    {
        'section': 'expenses',
        'lda_question': '14',
        'field': 'expense_method_b',
        'path': '/html/body/table[4]/tbody/tr[7]/td[2]/p[1]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'expenses',
        'lda_question': '14',
        'field': 'expense_method_c',
        'path': '/html/body/table[4]/tbody/tr[7]/td[2]/p[2]/input',
        'parser': checkbox_boolean
    },
    {
        'section': 'signature',
        'lda_question': None,
        'field': 'signature',
        'path': '/html/body/table[5]/tbody/tr/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'signature',
        'lda_question': None,
        'field': 'signature_date',
        'path': '/html/body/table[5]/tbody/tr/td[4]/div',
        'parser': parse_datetime
    },
    {
        'section': 'lobbying_activities',
        'lda_question': None,
        'field': 'lobbying_activities',
        'path': '//p[contains(.,"15. General issue area")]',
        'parser': parse_array,
        'children': [
            {
                'section': 'lobbying_activities',
                'lda_question': '15',
                'field': 'general_issue_area',
                'path': 'following-sibling::p[1]',
                'parser': split_keep_rightmost
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '16',
                'field': 'specific_issues',
                'path': 'following-sibling::p[2]',
                'parser': split_keep_rightmost
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '17',
                'field': 'houses_and_agencies_none',
                'path': 'following-sibling::p[3]/span/input',
                'parser': checkbox_boolean
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '17',
                'field': 'houses_and_agencies',
                'path': 'following-sibling::p[4]',
                'parser': clean_text
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '18',
                'field': 'lobbyists',
                'path': 'following-sibling::table[1]/tbody/tr[position() > 1]',
                'parser': parse_array,
                'children': [
                    {
                        'section': 'lobbying_activities',
                        'lda_question': '18',
                        'field': 'lobbyist_first_name',
                        'path': 'td[1]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'lobbying_activities',
                        'lda_question': '18',
                        'field': 'lobbyist_last_name',
                        'path': 'td[2]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'lobbying_activities',
                        'lda_question': '18',
                        'field': 'lobbyist_suffix',
                        'path': 'td[3]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'lobbying_activities',
                        'lda_question': '18',
                        'field': 'lobbyist_covered_position',
                        'path': 'td[4]/div',
                        'parser': clean_text
                    },
                    {
                        'section': 'lobbying_activities',
                        'lda_question': '18',
                        'field': 'lobbyist_is_new',
                        'path': 'td[5]/input',
                        'parser': checkbox_boolean
                    }
                ]
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '19',
                'field': 'foreign_entity_interest_none',
                'path': 'following-sibling::p[6]/span/input',
                'parser': checkbox_boolean
            },
            {
                'section': 'lobbying_activities',
                'lda_question': '19',
                'field': 'foreign_entity_interest',
                'path': 'following-sibling::p[7]',
                'parser': clean_text
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 20,
        'field': 'client_new_address',
        'path': '//p[contains(.,"20. Client new address")]/following-sibling::table[1]/tbody/tr[1]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 20,
        'field': 'client_new_city',
        'path': '//p[contains(.,"20. Client new address")]/following-sibling::table[1]/tbody/tr[2]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 20,
        'field': 'client_new_state',
        'path': '//p[contains(.,"20. Client new address")]/following-sibling::table[1]/tbody/tr[2]/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 20,
        'field': 'client_new_zip',
        'path': '//p[contains(.,"20. Client new address")]/following-sibling::table[1]/tbody/tr[2]/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 20,
        'field': 'client_new_country',
        'path': '//p[contains(.,"20. Client new address")]/following-sibling::table[1]/tbody/tr[2]/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 21,
        'field': 'client_new_ppb_city',
        'path': '//p[contains(.,"21. Client new principal place")]/following-sibling::table[1]/tbody/tr[1]/td[2]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 21,
        'field': 'client_new_ppb_state',
        'path': '//p[contains(.,"21. Client new principal place")]/following-sibling::table[1]/tbody/tr[1]/td[4]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 21,
        'field': 'client_new_ppb_zip',
        'path': '//p[contains(.,"21. Client new principal place")]/following-sibling::table[1]/tbody/tr[1]/td[6]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 21,
        'field': 'client_new_ppb_country',
        'path': '//p[contains(.,"21. Client new principal place")]/following-sibling::table[1]/tbody/tr[1]/td[8]/div',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 22,
        'field': 'client_new_general_description',
        'path': '//p[contains(.,"22. New General description")]/following-sibling::div[1]',
        'parser': clean_text
    },
    {
        'section': 'registration_update',
        'lda_question': 23,
        'field': 'removed_lobbyists',
        'path': '//p[contains(.,"23. Name of each previously")]/following-sibling::table[1]/tbody/tr[position()>1]/td/table/tbody',
        'parser': parse_array,
        'children': [
            {
                'section': 'registration_update',
                'lda_question': 23,
                'field': 'removed_lobbyist_first_name',
                'path': 'td[1]/div',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': 23,
                'field': 'removed_lobbyist_last_name',
                'path': 'td[2]/div',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': 23,
                'field': 'removed_lobbyist_last_name',
                'path': 'td[3]/div',
                'parser': clean_text
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 24,
        'field': 'removed_lobbying_issues',
        'path': '//p[contains(.,"24. General lobbying issue")]/following-sibling::table[1]/tbody/tr/td/div',
        'parser': parse_array,
        'children': [
            {
                'section': 'lobbying_issues',
                'lda_question': '24',
                'field': 'issue_code',
                'path': '.',
                'parser': clean_text
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 25,
        'field': 'added_affiliated_organizations',
        'path': '//p[contains(.,"25. Add the following")]/following-sibling::table[1]/tbody/tr',
        'parser': parse_array,
        'children': [
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_name',
                'path': 'td[1]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_address',
                'path': 'td[2]/table/tbody/tr[1]/td',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_city',
                'path': 'td[2]/table/tbody/tr[2]/td[1]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_state',
                'path': 'td[2]/table/tbody/tr[2]/td[2]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_zip',
                'path': 'td[2]/table/tbody/tr[2]/td[3]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_country',
                'path': 'td[2]/table/tbody/tr[2]/td[4]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_ppb_city',
                'path': 'td[3]/table/tbody/tr[1]/td',
                'parser': split_keep_rightmost
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_ppb_state',
                'path': 'td[3]/table/tbody/tr[2]/td[1]',
                'parser': split_keep_rightmost
            },
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_ppb_country',
                'path': 'td[3]/table/tbody/tr[2]/td[2]',
                'parser': split_keep_rightmost
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 26,
        'field': 'removed_affiliated_organizations',
        'path': '//p[contains(.,"26. Name of each previously")]/following-sibling::table[1]/tbody/tr/td/span',
        'parser': parse_array,
        'children': [
            {
                'section': 'registration_update',
                'lda_question': '25',
                'field': 'affiliated_organization_name',
                'path': '.',
                'parser': tail_text 
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 27,
        'field': 'added_foreign_entities',
        'path': '//p[contains(.,"27. Add the following foreign")]/following-sibling::table[1]/tbody/tr',
        'parser': parse_array,
        'children': [
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_name',
                'path': 'td[1]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_address',
                'path': 'td[2]/table/tbody/tr[1]/td[1]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_city',
                'path': 'td[2]/table/tbody/tr[2]/td[1]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_state',
                'path': 'td[2]/table/tbody/tr[2]/td[2]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_country',
                'path': 'td[2]/table/tbody/tr[2]/td[3]',
                'parser': clean_text
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_ppb_city',
                'path': 'td[3]/table/tbody/tr[1]/td',
                'parser': split_keep_rightmost
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_ppb_state',
                'path': 'td[3]/table/tbody/tr[2]/td[1]',
                'parser': split_keep_rightmost
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_ppb_country',
                'path': 'td[3]/table/tbody/tr[2]/td[2]',
                'parser': split_keep_rightmost
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_amount',
                'path': 'td[4]',
                'parser': parse_decimal
            },
            {
                'section': 'registration_update',
                'lda_question': '27',
                'field': 'foreign_entity_ownership_percentage',
                'path': 'td[5]',
                'parser': parse_percent
            },
        ]
    },
    {
        'section': 'registration_update',
        'lda_question': 28,
        'field': 'removed_affiliated_organizations',
        'path': '//p[contains(.,"28. Name of each previously reported foreign entity")]/following-sibling::table[1]/tbody/tr/td/span',
        'parser': parse_array,
        'children': [
            {
                'section': 'registration_update',
                'lda_question': '28',
                'field': 'foreign_entity_name',
                'path': '.',
                'parser': tail_text
            },
        ]
    },
]
