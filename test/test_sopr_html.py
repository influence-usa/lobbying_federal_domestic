
# coding: utf-8

# In[212]:

import json
import os
import re
import sys
import urlparse

from datetime import datetime, date, timedelta
from collections import defaultdict
from io import StringIO
from glob import glob

import requests
from pyquery import PyQuery as pq

from lxml import etree

import settings

from tasks import extract
from tasks.schema import ld1_schema, ld2_schema
from tasks.utils import mkdir_p, translate_dir


FILING_DETAIL_URL = 'http://soprweb.senate.gov/index.cfm?'
html_parser = etree.HTMLParser()

# In[214]:

test_set_defs = {
    'sopr_html': {'ld1':
                  [
                      {
                          'test_name': 'random',
                          'event': 'getFilingDetails',
                          'filingID': 'b4c3bd67-7c7c-45e6-8b6c-5fd6b55eec3f',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'multiple_lobbyists',
                          'event': 'getFilingDetails',
                          'filingID': 'C3A7E902-87A2-49FB-8D27-1D031F48DC12',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'multiple_lobbying_issues',
                          'event': 'getFilingDetails',
                          'filingID': '3A144627-84A0-4190-81A8-B40718EA37EC',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'multiple_affiliated_orgs',
                          'event': 'getFilingDetails',
                          'filingID': 'C3A7E902-87A2-49FB-8D27-1D031F48DC12',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'multiple_issues',
                          'event': 'getFilingDetails',
                          'filingID': '3A144627-84A0-4190-81A8-B40718EA37EC',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'multiple_foreign_entities',
                          'event': 'getFilingDetails',
                          'filingID': '3A144627-84A0-4190-81A8-B40718EA37EC',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'index_out_of_range',
                          'event': 'getFilingDetails',
                          'filingID': 'b1170146-00ac-4186-ba9b-01da020446ea',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'date_bad',
                          'event': 'getFilingDetails',
                          'filingID': 'e6349365-11de-48b3-9c56-c3917595b56f',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'date_mdy',
                          'event': 'getFilingDetails',
                          'filingID': '57702f25-d4bb-465a-b654-d1b8aedec3fa',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'date_m-d-y',
                          'event': 'getFilingDetails',
                          'filingID': '770967dd-e25a-4bfc-ad06-749132db4525',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'date_m-d-Y',
                          'event': 'getFilingDetails',
                          'filingID': '7e0c83ac-577a-48ae-83ee-ec4ebaf3964d',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'date_Ymd',
                          'event': 'getFilingDetails',
                          'filingID': '308f6aaa-c292-440e-8eca-f49fa937758e',
                          'filingTypeID': 1
                      },
                      {
                          'test_name': 'self_employed',
                          'event': 'getFilingDetails',
                          'filingID': 'b931620a-16aa-4834-b798-e08b0a3bddf8',
                          'filingTypeID': 1
                      }
                  ],
                  'ld2':
                  [
                      {
                          'test_name': 'multiple_issues',
                          'event': 'getFilingDetails',
                          'filingID': '80b956e1-3448-404a-bdfd-558ffe2631ce',
                          'filingTypeID': 69
                      },
                      {
                          'test_name': 'multiple_added_affiliated',
                          'event': 'getFilingDetails',
                          'filingID': '42524728-28e1-424f-9608-2b4f05f7cd2b',
                          'filingTypeID': 82
                      },
                      {
                          'test_name': 'multiple_removed_affiliated',
                          'event': 'getFilingDetails',
                          'filingID': '2897035b-c56e-4d05-9a51-cab6a4b505f8',
                          'filingTypeID': 53
                      },
                      {
                          'test_name': 'multiple_added_foreign',
                          'event': 'getFilingDetails',
                          'filingID': '6e8effc6-e1e3-413e-86c9-24eda20858f2',
                          'filingTypeID': 60
                      },
                      {
                          'test_name': 'neither_expense',
                          'event': 'getFilingDetails',
                          'filingID': '0005b52d-cd4e-4e4a-984f-7ade8e95eaa8',
                          'filingTypeID': 53
                      },
                      {
                          'test_name': 'multiple_inactive_foreign',
                          'event': 'getFilingDetails',
                          'filingID': '55dd2926-23b4-489d-8132-b040cc6ddac5',
                          'filingTypeID': 78
                      }]}}


def download_html_file(params):
    resp = requests.get(FILING_DETAIL_URL, params=params)
    return resp.content


def build_test_sets(source_name):
    for form, test_cases in test_set_defs[source_name].iteritems():
        _test_data_dir = os.path.join(settings.TEST_CACHE_DIR,
                                      source_name, form)
        if not os.path.exists(_test_data_dir):
            mkdir_p(_test_data_dir)
        for test_case in test_cases:
            filename = test_case.pop('test_name') + '.html'
            content = download_html_file(test_case)
            with open(os.path.join(_test_data_dir, filename), 'wb') as fout:
                fout.write(content)


if __name__ == "__main__":
    build_test_sets('sopr_html')

    ld1_cache_paths = glob(os.path.join(settings.TEST_CACHE_DIR, 'sopr_html',
                                        'ld1', '*.html'))
    ld1_containers = filter(lambda x: 'children' in x, ld1_schema)
    ld1_elements = filter(lambda x: 'children' not in x, ld1_schema)
    
    ld2_cache_paths = glob(os.path.join(settings.TEST_CACHE_DIR, 'sopr_html',
                                        'ld2', '*.html'))
    ld2_containers = filter(lambda x: 'children' in x, ld2_schema)
    ld2_elements = filter(lambda x: 'children' not in x, ld2_schema)
    
    options = {}
    options['test'] = True
    extract.extract_all_html(ld1_cache_paths, ld1_elements, ld1_containers, options)
    extract.extract_all_html(ld2_cache_paths, ld2_elements, ld2_containers, options)
