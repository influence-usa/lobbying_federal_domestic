import os
import sys
import json
import logging
from glob import glob, iglob
import uuid
from datetime import datetime
from copy import deepcopy

from multiprocessing import Pool as ThreadPool

from lxml import etree

import settings as s
from utils import translate_dir, map_vals, get_key
from utils import set_up_logging
import ref.ocd

log = set_up_logging('transform', loglevel=logging.DEBUG)


def ocd_id(prefix):
    return prefix + '/' + str(uuid.uuid1())


def log_result(result):
    if result[0] == 'success':
        src_dir, dest_dir = result[1:]
        log.info("successfully extracted " +
                 "{src_dir} => {dest_dir}".format(
                     src_dir=src_dir, dest_dir=dest_dir))
    elif result[0] == 'failure':
        loc, e = result[1:]
        log.error("extracting from {loc} failed: {exception}".format(
            loc=loc, exception=str(e)))
    else:
        raise Exception('Result for {loc} was neither success nor failure?')


def transform_sopr_xml(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    def _is_array(element):
        return element.getchildren() != []

    def _add_element_single(element, json_dict):
        json_dict[element.tag] = dict(element.attrib)

    def _add_element_array(root_node, json_dict):
        json_dict[root_node.tag] = []
        for e in root_node.getchildren():
            json_dict[root_node.tag].append(dict(e.attrib))

    def _add_element(element, json_dict):
        if _is_array(element):
            _add_element_array(element, json_dict)
        else:
            _add_element_single(element, json_dict)

    def _write_to_file(xml_filepath, filing):
        path, destination_dir = translate_dir(xml_filepath,
                                              from_dir=s.ORIG_DIR,
                                              to_dir=s.TRANS_DIR)
        filing_id = json_filing['ID']
        output_path = os.path.join(destination_dir,
                                   '{fid}.json'.format(fid=filing_id))
        if os.path.exists(output_path) and not options['force']:
            raise OSError(os.errno.EEXIST,
                          ' '.join([os.strerror(os.errno.EEXIST)+':',
                                    output_path]))

        with open(output_path, 'w') as output_file:
            json.dump(json_filing, output_file)

    all_fields = ['AffiliatedOrgs',
                  'Client',
                  'ForeignEntities',
                  'GovernmentEntities',
                  'Issues',
                  'Lobbyists',
                  'Registrant']

    xml_files = glob(os.path.join(s.ORIG_DIR, 'sopr_xml/*/*/*.xml'))

    for xml_filepath in xml_files:
        for filing in etree.parse(open(xml_filepath)).getroot().iterchildren():
            json_filing = dict.fromkeys(all_fields)
            json_filing.update(dict(filing.attrib))

            for element in filing.getchildren():
                _add_element(element, json_filing)

            _write_to_file(xml_filepath, json_filing)


def transform_house_xml(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    ARRAY_FIELDS = ['inactiveOrgs',
                    'inactive_lobbyists',
                    'federal_agencies',
                    'inactive_ALIs',
                    'lobbyists',
                    'affiliatedOrgs',
                    'alis',
                    'specific_issues',
                    'foreignEntities',
                    'inactive_ForeignEntities']

    def _add_element_array(children, json_array):
        for c in children:
            new_obj = _add_element(c, {})
            json_array.append(new_obj[c.tag])

    def _add_element(element, json_dict):
        children = element.getchildren()
        if children:
            if element.tag in ARRAY_FIELDS:
                json_dict[element.tag] = []
                _add_element_array(children, json_dict[element.tag])
            else:
                json_dict[element.tag] = {}
                for child in children:
                    _add_element(child, json_dict[element.tag])
        else:
            text = element.text or ''
            json_dict[element.tag] = text.strip()
        return json_dict

    def _write_to_file(xml_filepath, json_filing):
        path, destination_dir = translate_dir(xml_filepath,
                                              from_dir=s.ORIG_DIR,
                                              to_dir=s.TRANS_DIR)
        filing_id = os.path.splitext(os.path.basename(xml_filepath))[0]
        output_path = os.path.join(destination_dir,
                                   '{fid}.json'.format(fid=filing_id))
        if os.path.exists(output_path) and not options['force']:
            raise OSError(os.errno.EEXIST,
                          ' '.join([os.strerror(os.errno.EEXIST)+':',
                                    output_path]))

        with open(output_path, 'w') as output_file:
            json.dump(json_filing, output_file)

    xml_files = glob(os.path.join(s.ORIG_DIR, 'house_xml/*/*/*/*.xml'))

    for xml_filepath in xml_files:
        try:
            et = etree.parse(open(xml_filepath))
            filing = et.getroot()
            json_filing = _add_element(filing, {})
            _write_to_file(xml_filepath, json_filing)
        except Exception as e:
            log.error(str(e)+' ('+xml_filepath+')')
        except etree.XMLSyntaxError as x:
            log.error(str(x)+' ('+xml_filepath+')')


def transform_sopr_html(options):

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    def _write_to_file(original_fileloc, json_filing):
        _path, destination_dir = translate_dir(original_fileloc,
                                               from_dir=s.ORIG_DIR,
                                               to_dir=s.TRANS_DIR)
        filing_id = json_filing['disclosure']['id'].split('/')[1]
        output_path = os.path.join(destination_dir,
                                   '{fid}.json'.format(fid=filing_id))

        if os.path.exists(output_path) and not options['force']:
            raise OSError(os.errno.EEXIST,
                          ' '.join([os.strerror(os.errno.EEXIST)+':',
                                    output_path]))

        with open(output_path, 'w') as output_file:
            json.dump(json_filing, output_file)

        return output_path

    def _determine_quarter(record):
        report = record['report_type'].copy()
        quarter_map = {'one': 'Q1',
                       'two': 'Q2',
                       'three': 'Q3',
                       'four': 'Q4'}
        quarter = [v for q, v in quarter_map.items()
                   if report['quarter_'+q]]
        assert len(quarter) <= 1
        try:
            return quarter[0]
        except IndexError:
            return None

    def _determine_expense_method(record):
        expenses = record['expenses'].copy()

        method_labels = ['a', 'b', 'c']

        method = [l for l in method_labels if expenses['expense_method_'+l]]
        assert len(method) <= 1
        try:
            return method[0]
        except IndexError:
            return None

    def _determine_expense_lt(original_ld2):
        if get_key(original_ld2, 'expenses.expense_less_than_five_thousand'):
            return True
        elif get_key(original_ld2, 'expenses.expense_five_thousand_or_more'):
            return False
        else:
            return None

    def _determine_income_lt(original_ld2):
        if get_key(original_ld2, 'income.income_less_than_five_thousand'):
            return True
        elif get_key(original_ld2, 'income.income_five_thousand_or_more'):
            return False
        else:
            return None

    def _pop_true(dictlike):
        for k, v in dictlike.iteritems():
            if v:
                return k
        else:
            return None

    def _transform_foreign_entity(fe):
        fe['foreign_entity_amount'] = \
            float(fe.pop('foreign_entity_amount', 0.0))
        fe['foreign_entity_ownership_percentage'] = \
            float(fe.pop('foreign_entity_ownership_percentage', 0.0)) / 100.0
        return fe

    def _postprocess_ld2(transformed_ld2, original_ld2):
        _transformed_ld2 = transformed_ld2.copy()
        _transformed_ld2['report_type']['quarter'] = _determine_quarter(original_ld2)
        _transformed_ld2['expense_reporting_method'] = _determine_expense_method(original_ld2)
        if get_key(original_ld2, 'report_type.no_activity'):
            _transformed_ld2['lobbying_activities'] = []
        _transformed_ld2['expense_less_than_five_thousand'] = _determine_expense_lt(original_ld2)
        _transformed_ld2['income_less_than_five_thousand'] = _determine_income_lt(original_ld2)
        return _transformed_ld2

    def _registration_name(orig_json):
        if orig_json['registration_type']['new_registrant']:
            regtype = 'New Client, New Registrant'
        elif orig_json['registration_type']['is_amendment']:
            regtype = 'Amended Registration'
        else:
            regtype = 'New Client'
        return regtype

    def _ocdize_ld1(original_ld1):
        _orig = original_ld1.copy()

        # TODO decide on tz
        fake_now = datetime.now()

        # basic disclosure fields
        _disclosure = deepcopy(ref.ocd.OCD_DISCLOSURE)
        _disclosure['id'] = 'ocd-disclosure/{}'.format(_orig['document_id'])
        _disclosure['effective_date'] = _orig['datetimes']['effective_date']
        _disclosure['created_at'] = fake_now.isoformat()
        _disclosure['updated_at'] = None
        _disclosure['authority'] = ref.ocd.SOPR['name'][:]
        _disclosure['authority_id'] = ref.ocd.SOPR['id'][:]

        # disclosure extras
        _disclosure['extras'] = deepcopy(ref.ocd.SOPR_LD1_EXTRAS)
        _disclosure['extras']['registrant'].update({
            'self_employed_individual':
                _orig['registrant']['self_employed_individual'],
            'general_description':
                _orig['registrant']['registrant_general_description'],
            'signature': {
                "signature_date": _orig['signature']['signature_date'],
                "signature": _orig['signature']['signature']}
        })

        _disclosure['extras']['client'].update({
            'same_as_registrant':
                _orig['client']['client_self'],
            'general_description':
                _orig['client']['client_general_description']
        })

        _disclosure['extras']['registration_type'].update({
            'is_amendment':
                _orig['registration_type']['is_amendment'],
            'new_registrant':
                _orig['registration_type']['new_registrant'],
            'new_client_for_existing_registrant':
                _orig['registration_type']['new_client_for_existing_registrant'],
        })

        # # Registrant
        # build registrant
        if _orig['registrant']['self_employed_individual']:
            _registrant = deepcopy(ref.ocd.OCD_PERSON)
            _registrant['id'] = ocd_id('ocd-person')
            _registrant['name'] = ' '.join(
                [p for p in [
                    _orig['registrant']['registrant_individual_prefix'],
                    _orig['registrant']['registrant_individual_firstname'],
                    _orig['registrant']['registrant_individual_lastname']]
                 if len(p) > 0])
        else:
            _registrant = deepcopy(ref.ocd.OCD_ORGANIZATION)
            _registrant['id'] = ocd_id('ocd-organization')
            _registrant['name'] = _orig['registrant']['registrant_org_name']
            _registrant['classification'] = 'corporation'

        for scheme, ident in _orig['identifiers'].iteritems():
            _registrant['identifiers'].append({
                'scheme': 'LDA/{}'.format(scheme),
                'identifier': ident
            })

        _registrant['contact_details'] = [
            {
                "type": "address",
                "label": "contact address",
                "value": '; '.join([
                    p for p in [
                        _orig['registrant']['registrant_address_one'],
                        _orig['registrant']['registrant_address_two'],
                        _orig['registrant']['registrant_city'],
                        _orig['registrant']['registrant_state'],
                        _orig['registrant']['registrant_zip'],
                        _orig['registrant']['registrant_country']]
                    if len(p) > 0]),
                "note": _orig['registrant']['registrant_contact_name']
            },
            {
                "type": "address",
                "label": "principal place of business",
                "value": '; '.join([
                    p for p in [
                        _orig['registrant']['registrant_ppb_city'],
                        _orig['registrant']['registrant_ppb_state'],
                        _orig['registrant']['registrant_ppb_zip'],
                        _orig['registrant']['registrant_ppb_country']]
                    if len(p) > 0]),
                "note": _orig['registrant']['registrant_contact_name']
            },
            {
                "type": "phone",
                "label": "contact phone",
                "value": _orig['registrant']['registrant_contact_phone'],
                "note": _orig['registrant']['registrant_contact_name']
            },
            {
                "type": "email",
                "label": "contact email",
                "value": _orig['registrant']['registrant_contact_email'],
                "note": _orig['registrant']['registrant_contact_name']
            },
        ]

        _registrant["extras"] = {
            "contact_details_structured": [
                {
                    "type": "address",
                    "label": "contact address",
                    "parts": [
                        {
                            "label": "address_one",
                            "value": _orig['registrant']['registrant_address_one'],
                        },
                        {
                            "label": "address_two",
                            "value": _orig['registrant']['registrant_address_two'],
                        },
                        {
                            "label": "city",
                            "value": _orig['registrant']['registrant_city'],
                        },
                        {
                            "label": "state",
                            "value": _orig['registrant']['registrant_state'],
                        },
                        {
                            "label": "zip",
                            "value": _orig['registrant']['registrant_zip'],
                        },
                        {
                            "label": "country",
                            "value": _orig['registrant']['registrant_country'],
                        }
                    ],
                    "note": "registrant contact on SOPR LD-1"
                },
                {
                    "type": "address",
                    "label": "principal place of business",
                    "parts": [
                        {
                            "label": "city",
                            "value": _orig['registrant']['registrant_ppb_city'],
                        },
                        {
                            "label": "state",
                            "value": _orig['registrant']['registrant_ppb_state'],
                        },
                        {
                            "label": "zip",
                            "value": _orig['registrant']['registrant_ppb_zip'],
                        },
                        {
                            "label": "country",
                            "value": _orig['registrant']['registrant_ppb_country'],
                        }
                    ],
                    "note": "registrant contact on SOPR LD-1"
                },
            ]
        }

        # add registrant
        _disclosure['registrant'] = _registrant['name']
        _disclosure['registrant'] = _registrant['id']

        # # People
        # build contact
        _main_contact = deepcopy(ref.ocd.OCD_ORGANIZATION)
        _main_contact['id'] = ocd_id('ocd-person')
        _main_contact['name'] = \
            _orig['registrant']['registrant_contact_name']
        _main_contact['contact_details'] = [
            {
                "type": "phone",
                "label": "contact phone",
                "value": _orig['registrant']['registrant_contact_phone'],
                "note": _orig['registrant']['registrant_org_name']
            },
            {
                "type": "email",
                "label": "contact email",
                "value": _orig['registrant']['registrant_contact_email'],
                "note": _orig['registrant']['registrant_org_name']
            }
        ]
        _main_contact_membership = deepcopy(ref.ocd.OCD_MEMBERSHIP)
        _main_contact_membership['organization'].update({
            'id': _registrant['id'],
            'classification': 'corporation',
            'name': _registrant['name']
        })
        _main_contact_membership['post'].update({
            'id': ocd_id('ocd-post'),
            'role': 'main_contact',
            'start_date': _orig['datetimes']['effective_date']
        })
        _main_contact['memberships'].append(_main_contact_membership)

        # # Client
        # build client
        _client = deepcopy(ref.ocd.OCD_ORGANIZATION)
        _client['id'] = ocd_id('ocd-organization')
        _client['name'] = _orig['client']['client_name']

        _client['contact_details'] = [
            {
                "type": "address",
                "label": "contact address",
                "value": '; '.join([
                    p for p in [
                        _orig['client']['client_address'],
                        _orig['client']['client_city'],
                        _orig['client']['client_state'],
                        _orig['client']['client_zip'],
                        _orig['client']['client_country']]
                    if len(p) > 0]),
                "note": _orig['client']['client_name']
            },
            {
                "type": "address",
                "label": "principal place of business",
                "value": '; '.join([
                    p for p in [
                        _orig['client']['client_ppb_city'],
                        _orig['client']['client_ppb_state'],
                        _orig['client']['client_ppb_zip'],
                        _orig['client']['client_ppb_country']]
                    if len(p) > 0]),
                "note": _orig['client']['client_name']
            },
        ],
        
        _client["extras"] = {
            "contact_details_structured": [
                {
                    "type": "address",
                    "label": "contact address",
                    "parts": [
                        {
                            "label": "address",
                            "value": _orig['client']['client_address'],
                        },
                        {
                            "label": "city",
                            "value": _orig['client']['client_city'],
                        },
                        {
                            "label": "state",
                            "value": _orig['client']['client_state'],
                        },
                        {
                            "label": "zip",
                            "value": _orig['client']['client_zip'],
                        },
                        {
                            "label": "country",
                            "value": _orig['client']['client_country'],
                        }
                    ],
                    "note": "client contact on SOPR LD-1"
                },
                {
                    "type": "address",
                    "label": "principal place of business",
                    "parts": [
                        {
                            "label": "city",
                            "value": _orig['client']['client_ppb_city'],
                        },
                        {
                            "label": "state",
                            "value": _orig['client']['client_ppb_state'],
                        },
                        {
                            "label": "zip",
                            "value": _orig['client']['client_ppb_zip'],
                        },
                        {
                            "label": "country",
                            "value": _orig['client']['client_ppb_country'],
                        }
                    ],
                    "note": "client contact on SOPR LD-1"
                },
            ],
        }

        _foreign_entities = []
        for fe in _orig['foreign_entities']['foreign_entities']:
            _foreign_entity = deepcopy(ref.ocd.OCD_ORGANIZATION)
            _foreign_entity['id'] = ocd_id('ocd-organization')
            _foreign_entity['name'] = fe['foreign_entity_name']
            _foreign_entity['contact_details'] = [
                {
                    "type": "address",
                    "label": "contact address",
                    "value": '; '.join([
                        p for p in [
                            fe['foreign_entity_address'],
                            fe['foreign_entity_city'],
                            fe['foreign_entity_state'],
                            fe['foreign_entity_country']]
                        if len(p) > 0]),
                },
                {
                    "type": "address",
                    "label": "principal place of business",
                    "value": '; '.join([
                        p for p in [
                            fe['foreign_entity_ppb_state'],
                            fe['foreign_entity_ppb_country']]
                        if len(p) > 0]),
                },
            ]
            _foreign_entity["extras"] = {
                "contact_details_structured": [
                    {
                        "type": "address",
                        "label": "contact address",
                        "parts": [
                            {
                                "label": "address",
                                "value": fe['foreign_entity_address'],
                            },
                            {
                                "label": "city",
                                "value": fe['foreign_entity_city'],
                            },
                            {
                                "label": "state",
                                "value": fe['foreign_entity_state'],
                            },
                            {
                                "label": "country",
                                "value": fe['foreign_entity_country'],
                            }
                        ],
                        "note": "foreign_entity contact on SOPR LD-1"
                    },
                    {
                        "type": "address",
                        "label": "principal place of business",
                        "parts": [
                            {
                                "label": "state",
                                "value": fe['foreign_entity_ppb_state'],
                            },
                            {
                                "label": "country",
                                "value": fe['foreign_entity_ppb_country'],
                            }
                        ],
                        "note": "foreign_entity contact on SOPR LD-1"
                    },
                ],
            }

            _client['memberships'].append({
                "id": _foreign_entity['id'],
                "classification": "organization",
                "name": _foreign_entity['name'],
                "extras": {
                    "ownership_percentage":
                        fe['foreign_entity_amount']
                }
            })

            _foreign_entities.append(_foreign_entity)

        _lobbyists = []
        for l in _orig['lobbyists']['lobbyists']:
            _lobbyist = deepcopy(ref.ocd.OCD_PERSON)
            _lobbyist['name'] = ' '.join([
                l['lobbyist_first_name'],
                l['lobbyist_last_name'],
                l['lobbyist_suffix'],
            ])
            _lobbyist['id'] = ocd_id('person')
            _lobbyist['extras']['lda_covered_official_positions'] = []
            if l['lobbyist_covered_official_position']:
                _lobbyist['extras']['lda_covered_official_positions'].append({
                    'date_reported':
                        _orig['datetimes']['effective_date'],
                    'disclosure_id':
                        _disclosure['id'],
                    'covered_official_position':
                        l['lobbyist_covered_official_position'],
                })
            _lobbyist_membership = deepcopy(ref.ocd.OCD_MEMBERSHIP)
            _lobbyist_membership['organization'].update({
                'id': _registrant['id'],
                'classification': 'corporation',
                'name': _registrant['name']
            })
            _lobbyist_membership['post'].update({
                'id': ocd_id('ocd-post'),
                'role': 'lobbyist',
                'start_date': _orig['datetimes']['effective_date']
            })
            _lobbyist['memberships'].append(_lobbyist_membership)
            _lobbyists.append(_lobbyist)

        # # Document
        # build document
        _document = deepcopy(ref.ocd.OCD_DOCUMENT)
        _document['note'] = 'submitted filing'
        _document['date'] = _orig['datetimes']['effective_date']
        _document['links'] = []

        # add document
        _disclosure['documents'].append(_document)

        # Affiliated orgs
        _affiliated_organizations = []
        for ao in _orig['affiliated_organizations']['affiliated_organizations']:
            _affiliated_organization = deepcopy(ref.ocd.OCD_ORGANIZATION)
            _affiliated_organization['id'] = ocd_id('ocd-organization')
            _affiliated_organization['name'] = \
                ao['affiliated_organization_name']
            _affiliated_organization['contact_details'] = [
                {
                    "type": "address",
                    "label": "contact address",
                    "value": '; '.join([
                        p for p in [
                            ao['affiliated_organization_address'],
                            ao['affiliated_organization_city'],
                            ao['affiliated_organization_state'],
                            ao['affiliated_organization_zip'],
                            ao['affiliated_organization_country']]
                        if len(p) > 0]),
                },
                {
                    "type": "address",
                    "label": "principal place of business",
                    "value": '; '.join([
                        p for p in [
                            ao['affiliated_organization_ppb_city'],
                            ao['affiliated_organization_ppb_state'],
                            ao['affiliated_organization_ppb_country']]
                        if len(p) > 0]),
                },
            ]
            _affiliated_organization["extras"] = {
                "contact_details_structured": [
                    {
                        "type": "address",
                        "label": "contact address",
                        "parts": [
                            {
                                "label": "address",
                                "value": ao['affiliated_organization_address'],
                            },
                            {
                                "label": "city",
                                "value": ao['affiliated_organization_city'],
                            },
                            {
                                "label": "state",
                                "value": ao['affiliated_organization_state'],
                            },
                            {
                                "label": "zip",
                                "value": ao['affiliated_organization_zip'],
                            },
                            {
                                "label": "country",
                                "value": ao['affiliated_organization_country'],
                            }
                        ],
                        "note": "affiliated organization contact on SOPR LD-1"
                    },
                    {
                        "type": "address",
                        "label": "principal place of business",
                        "parts": [
                            {
                                "label": "city",
                                "value": ao['affiliated_organization_ppb_city'],
                            },
                            {
                                "label": "state",
                                "value": ao['affiliated_organization_ppb_state'],
                            },
                            {
                                "label": "country",
                                "value": ao['affiliated_organization_ppb_country'],
                            }
                        ],
                        "note": "affiliated organization contact on SOPR LD-1"
                    },
                ],
            }
            _affiliated_organizations.append(_affiliated_organization)

        # # Events & Agendas
        # name (TODO: make fct for name gen)
        # start
        # client-reg registration (w/ issue codes/detail)
        # client-reg-lobbyist registration
        # build lobbyists on the fly
        _event = deepcopy(ref.ocd.OCD_DISCLOSED_EVENT)
        _event['id'] = ocd_id('ocd-event')
        _event['name'] = _registration_name(_orig)
        _event['start_time'] = _orig['datetimes']['effective_date']
        _event['documents'].append(_document)
        if _orig['registrant']['self_employed_individual']:
            _event['participants'].append({
                "entity_type": "person",
                "id": _registrant['id'],
                "name": _registrant['name'],
                "note": "registrant"
            })
            _event['participants'].append({
                "entity_type": "person",
                "id": _registrant['id'],
                "name": _registrant['name'],
                "note": "lobbyist"
            })
        else:
            _event['participants'].append({
                "entity_type": "organization",
                "id": _registrant['id'],
                "name": _registrant['name'],
                "note": "registrant"
            })

        _event['participants'].append({
            "entity_type": "organization",
            "id": _client['id'],
            "name": _client['name'],
            "note": "client"
        })

        for l in _lobbyists:
            _event['participants'].append({
                "entity_type": "person",
                "id": l['id'],
                "name": l['name'],
                "note": "lobbyist"
            })

        for fe in _foreign_entities:
            _event['participants'].append({
                "entity_type": "organization",
                "id": fe['id'],
                "name": fe['name'],
                "note": "foreign_entity"
            })

        for ao in _affiliated_organizations:
            _event['participants'].append({
                "entity_type": "organization",
                "id": ao['id'],
                "name": ao['name'],
                "note": "affiliated_organization"
            })

        _agenda = deepcopy(ref.ocd.OCD_AGENDA_ITEM)
        _agenda['notes'].append(
            _orig['lobbying_issues_detail']['lobbying_issues_detail'])
        for li in _orig['lobbying_issues']['lobbying_issues']:
            _agenda['subjects'].append(li['general_issue_area'])

        _disclosure['disclosed_events'].append(_event)
        return {'disclosure': _disclosure.copy(),
                'registrant': _registrant.copy(),
                'client': _client.copy(),
                'lobbyists': [l.copy() for l in _lobbyists],
                'main_contact': _main_contact.copy(),
                'affiliated_organizations': [a.copy() for a in _affiliated_organizations],
                'foreign_entities': [fe.copy() for fe in _foreign_entities]
                }

    def _postprocess_ld1(transformed_ld1, original_ld1):
        return transformed_ld1

    def _transform(original_loc, ocd_fct):
        try:
            with open(original_loc, 'r') as _original:
                _original_json = json.load(_original)
                _transformed = ocd_fct(_original_json)
                output_path = _write_to_file(original_loc, _transformed)
            return ('success', original_loc, output_path)
        except Exception as e:
            raise e
            #return ('failure', original_loc, e)

    def _transform_all(original_locs, ocd_fct, options):
        threaded = options.get('threaded', False)
        thread_num = options.get('thread_num', 4)

        # #methods used can't be pickled, unfortunately
        # if threaded:
        #     pool = ThreadPool(thread_num)
        #     for original_loc in original_locs:
        #         pool.apply_async(_transform, args=(original_loc, copy_map,
        #                          postprocess, template), callback=log_result)
        #     pool.close()
        #     pool.join()
        # else:
        for original_loc in original_locs:
            log_result(_transform(original_loc, ocd_fct))

    original_ld1_files = iglob(os.path.join(s.ORIG_DIR, 'sopr_html', '*',
                                            'REG', '*.json'))

    # original_ld2_files = iglob(os.path.join(s.ORIG_DIR, 'sopr_html', '*',
    #                                        'Q[1-4]', '*.json'))

    log.info('Beginning LD-1 transforms')
    _transform_all(original_ld1_files, _ocdize_ld1, options)
    log.info('Finished LD-1 transforms')
    #log.info('Beginning LD-2 transforms')
    #_transform_all(original_ld2_files, ld2_copy_map, _postprocess_ld2,
    #               {'datetimes': {}, 'report_type': {}}, options)
    #log.info('Finished LD-2 transforms')
