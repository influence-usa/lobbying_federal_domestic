import os
import sys
import json
import logging
from glob import glob, iglob

from lxml import etree

import settings as s
from .utils import translate_dir, map_vals
from .log import set_up_logging

log = set_up_logging('transform', loglevel=logging.DEBUG)


def transform_sopr_xml(options):
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
    # (orig loc, transformed loc)
    ld2_copy_map = [ ('document_id',                                           'document_id'),
                     ('signature.signature',                                   'signature'),
                     ('report.report_year',                                    'report_year'),
                     ('report.report_is_amendment',                            'report_is_amendment'),
                     ('report.report_is_termination',                          'report_is_termination'),
                     ('report.report_no_activity',                             'report_no_activity'),
                     ('report.report_termination_date',                        'datetimes.termination_date'),
                     ('signature.signature_date',                              'datetimes.signature_date'),
                     ('registrant',                                            'registrant'), 
                     ('identifiers.client_registrant_house_id',                'client_registrant_house_id'),
                     ('identifiers.client_registrant_senate_id',               'client_registrant_senate_id'),
                     ('lobbying_activities.lobbying_activities',               'lobbying_activities'),
                     ('registration_update',                                   'registration_update'),
                     ('client',                                                'client'),
                     ('income.income_amount',                                  'income_amount'),
                     ('income.income_less_than_five_thousand',                 'income_less_than_five_thousand'),
                     ('expenses.expense_amount',                               'expense_amount'),
                     ('expenses.expense_less_than_five_thousand',              'expense_less_than_five_thousand'),]

    # (orig loc, transformed loc)
    ld1_copy_map = [ ('document_id',                                           'document_id'),
                     ('registration_type',                                     'registration_type'),
                     ('datetimes',                                             'datetimes'),
                     ('registrant',                                            'registrant'), 
                     ('identifiers.registrant_house_id',                       'registrant.registrant_house_id'),
                     ('identifiers.registrant_senate_id',                      'registrant.registrant_senate_id'),
                     ('lobbying_issues.lobbying_issues',                       'lobbying_issues'),
                     ('lobbying_issues_detail.lobbying_issues_detail',         'lobbying_issues_detail'),
                     ('lobbyists.lobbyists',                                   'lobbyists'),
                     ('client',                                                'client'),
                     ('affiliated_organizations.affiliated_organizations_url', 'affiliated_organizations_url'),
                     ('affiliated_organizations.affiliated_organizations',     'affiliated_organizations'),
                     ('foreign_entities.foreign_entities',                     'foreign_entities'),
                     ('signature.signature',                                   'signature'),
                     ('signature.signature_date',                              'datetimes.signature_date'),]

    def _write_to_file(original_fileloc, json_filing):
        _path, destination_dir = translate_dir(original_fileloc,
                                               from_dir=s.ORIG_DIR,
                                               to_dir=s.TRANS_DIR)
        filing_id = json_filing['document_id']
        output_path = os.path.join(destination_dir,
                                   '{fid}.json'.format(fid=filing_id))

        if os.path.exists(output_path) and not options['force']:
            raise OSError(os.errno.EEXIST,
                          ' '.join([os.strerror(os.errno.EEXIST)+':',
                                    output_path]))

        with open(output_path, 'w') as output_file:
            json.dump(json_filing, output_file)

    def _determine_quarter(record):
        report = record['report'].copy()
        quarter_map = {'one': 'Q1',
                       'two': 'Q2',
                       'three': 'Q3',
                       'four': 'Q4'}
        quarter = [v for q, v in quarter_map.items()
                   if report['report_quarter_'+q]]
        assert len(quarter) == 1
        return quarter[0]

    def _determine_expense_method(record):
        expenses = record['expenses'].copy()

        method_labels = ['a', 'b', 'c']

        method = [l for l in method_labels if expenses['expense_method_'+l]]
        assert len(method) == 1
        return method[0]

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

    original_ld1_files = iglob(os.path.join(s.ORIG_DIR, 'sopr_html', '*',
                                            'REG', '*.json'))

    original_ld2_files = iglob(os.path.join(s.ORIG_DIR, 'sopr_html', '*',
                                            'Q[1-4]', '*.json'))

    for ld1_loc in original_ld1_files:
        try:
            original_ld1 = json.load(open(ld1_loc, 'r'))
            transformed_ld1 = map_vals(ld1_copy_map, original_ld1)
            _write_to_file(ld1_loc, transformed_ld1)
        except Exception as e:
            log.error(str(e)+' ('+ld1_loc+')')
        except etree.XMLSyntaxError as x:
            log.error(str(x)+' ('+ld1_loc+')')

    for ld2_loc in original_ld2_files:
        try:
            original_ld2 = json.load(open(ld2_loc, 'r'))
            transformed_ld2 = map_vals(ld2_copy_map, original_ld2,
                                       {'datetimes': {}})
            transformed_ld2['report_quarter'] = _determine_quarter(original_ld2)
            transformed_ld2['expense_reporting_method'] = _determine_expense_method(original_ld2)
            _write_to_file(ld2_loc, transformed_ld2)
        except Exception as e:
            log.error(str(e)+' ('+ld2_loc+')')
        except etree.XMLSyntaxError as x:
            log.error(str(x)+' ('+ld2_loc+')')
