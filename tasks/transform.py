import os
import json
import logging
from glob import glob

from lxml import etree
from stream import ProcessPool, ThreadPool, QCollector
from stream import map, item

import settings as s
from .utils import translate_dir
from .log import set_up_logging

log = set_up_logging('transform', loglevel=logging.DEBUG)


def is_array(element):
    return element.getchildren() != []


def add_element(element, json_dict):
    json_dict[element.tag] = dict(element.attrib)


def add_element_array(root_node, json_dict):
    json_dict[root_node.tag] = [dict(e.attrib) for e in root_node.getchildren()]


def transform_sopr(options):
    raise Exception("WARNING: THIS HAS A CRAZY MEMORY LEAK THAT ISN'T FIXED YET -BL")
    def _split_into_filings(xml_filename):
        tree = etree.parse(xml_filename)
        root = tree.getroot()
        filings = root.getchildren()
        del tree
        del root
        return ((xml_filename, filing) for filing in filings)
            
    def _split_all_into_filings(xml_files):
        for xml_filename in xml_files:
            yield _split_into_filings(xml_filename)

    def _xml_node_to_json(filing):
        xml_filename, filing_node = filing

        json_filing = {}

        json_filing.update(filing_node.attrib)

        for field in filing_node.getchildren():
            if is_array(field):
                add_element_array(field, json_filing)
            else:
                add_element(field, json_filing)

        del filing_node

        return (xml_filename, json_filing)

    def _all_xml_nodes_to_json(filing_list):
        for filing in filing_list:
            yield _xml_node_to_json(filing)

    def _fan_out(filing_lists):
        for filing_list in filing_lists:
            yield filing_list

    def _write_to_file(filing):
        xml_filename, json_filing = filing
        path, destination_dir = translate_dir(xml_filename,
                                              from_dir=s.ORIG_DIR,
                                              to_dir=s.TRANS_DIR)
        filing_id = json_filing['ID']
        output_path = os.path.join(destination_dir,
                                   '{fid}.json'.format(fid=filing_id))
        if os.path.exists(output_path) and not options['force']:
            raise OSError(os.errno.EEXIST,
                          ' '.join([os.strerror(os.errno.EEXIST)+':',
                                    output_path]))

        with open(output_path,'w') as output_file:
            json.dump(json_filing, output_file)

        return (xml_filename, filing_id, output_path)

    def _write_all_to_files(json_filings):
        for json_filing in json_filings:
            yield _write_to_file(json_filing)

    xml_files = glob(os.path.join(s.ORIG_DIR, 'sopr/*/*/*.xml'))

    log.debug("{num} files to do".format(num=len(xml_files)))

    transformed = xml_files >> ThreadPool(_split_all_into_filings) \
                        >> ThreadPool(_all_xml_nodes_to_json) \
                        >> ThreadPool(_write_all_to_files)

    for xml_filename, filing_id, output_path in transformed:
        log.info("successfully transformed " +
                 "filing {filing_id} from {input_path} to {output}".format(
                     filing_id=filing_id, input_path=xml_filename,
                     output=output_path))

    for xml_file_name, exception in transformed.failure:
        log.error("transforming from {path} failed: {exception}".format(
            path=xml_file_name, exception=exception))
