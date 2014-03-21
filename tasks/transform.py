import os
import json
import logging
from glob import glob

from lxml import etree

import settings as s
from .utils import translate_dir
from .log import set_up_logging

log = set_up_logging('transform', loglevel=logging.DEBUG)


def transform_sopr(options):
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

    xml_files = glob(os.path.join(s.ORIG_DIR, 'sopr/*/*/*.xml'))

    for xml_filepath in xml_files:
        for filing in etree.parse(open(xml_filepath)).getroot().iterchildren():
            json_filing = dict.fromkeys(all_fields)
            json_filing.update(dict(filing.attrib))

            for element in filing.getchildren():
                _add_element(element, json_filing)

            _write_to_file(xml_filepath, json_filing)
