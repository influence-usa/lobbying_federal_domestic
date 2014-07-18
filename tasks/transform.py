import os
import sys
import json
import logging
from glob import glob

from lxml import etree

import settings as s
from .utils import translate_dir
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
