import os
import sys
import re
import logging
import time
from itertools import product
from multiprocessing.dummy import Pool as ThreadPool

import requests

from pyquery import PyQuery as pq
import cookielib

from settings import CACHE_DIR
from .utils import mkdir_p
from .log import set_up_logging

log = set_up_logging('download', loglevel=logging.DEBUG)


# GENERAL DOWNLOAD FUNCTIONS
def response_download(response, output_loc):
    if response.ok:
        try:
            with open(output_loc, 'wb') as output_file:
                for chunk in response.iter_content():
                    output_file.write(chunk)
            return response.headers['content-length']
        except Exception as e:
            log.error(e)
    else:
        log.error('response not okay: '+response.reason)
        raise Exception('didn''t work, trying again')


def log_result(result):
    if result[0] == 'success':
        url, loc, content_length = result[1:]
        log.info(
            'success: {source} => {dest}({size})'.format(
                source=url, dest=loc, size=content_length))
    elif result[0] == 'failure':
        url, loc, exception = result[1:]
        log.info(
            'failure: {source} => {dest}\n {e}'.format(
                source=url, dest=loc, e=str(exception)))
    else:
        raise Exception


def download(val, get_response_loc_pair):
    for i in xrange(5):
        _response, _loc = get_response_loc_pair(val)
        if is_not_cached(_response, _loc):
            try:
                content_length = response_download(_response, _loc)
                _url = _response.url
                return ('success', _url, _loc, content_length)
            except Exception:
                log.warn('{url} something went wrong, trying again ' +
                         '({code} - {reason})'.format(
                             url=_response.url,
                             code=_response.status_code,
                             reason=_response.reason))
                time.sleep(5)
        else:
            log.info('cached, not re-downloading')
            return('success', _url, _loc, 'cached')
    return ('failure', _response.url, _loc, '[{code}] {reason}'.format(
        code=_response.status_code, reason=_response.reason))


def download_all(vals, get_response_loc_pair, options):
    threaded = options.get('threaded', False)
    thread_num = options.get('thread_num', 4)

    if threaded:
        pool = ThreadPool(thread_num)
        for val in vals:
            pool.apply_async(download, args=(val, get_response_loc_pair),
                             callback=log_result)
        pool.close()
        pool.join()
    else:
        for val in vals:
            response_loc_pair = get_response_loc_pair(val)
            log_result(download(response_loc_pair))


def is_not_cached(response, output_loc):
    response, output_loc
    if os.path.exists(output_loc):
        downloaded_size = int(os.path.getsize(output_loc))
        log.debug(
            'found {output_loc}: {size}'.format(
                output_loc=output_loc,
                size=downloaded_size))
        size_on_server = int(response.headers['content-length'])
        if downloaded_size != size_on_server:
            log.debug(
                're-downloading {url}: {size}'.format(
                    url=response.url,
                    size=size_on_server))
            return True
        else:
            response.close()
            return False
    else:
        return True


# SPECIFIC TASKS
def download_sopr(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    def _get_response_loc_pair(url):
        fname = requests.utils.urlparse(url).path.split('/')[-1]
        year, quarter = fname.split('.')[0].split('_')
        output_dir = os.path.join(CACHE_DIR, 'sopr', year, 'Q' + quarter)
        if not os.path.exists(output_dir):
            mkdir_p(output_dir)
        output_loc = os.path.join(output_dir, fname)
        response = requests.get(url, stream=True)
        return (response, output_loc)

    _url_template = 'http://soprweb.senate.gov/downloads/{year}_{quarter}.zip'

    _urls = [_url_template.format(year=year, quarter=quarter)
             for year, quarter in
             product(xrange(1999, 2015), xrange(1, 5))]

    # response_loc_pairs = (_get_response_loc_pair(url) for url in _urls)    
    download_all(_urls, _get_response_loc_pair, options)

def download_sopr_report_types(options):
    FORM_URL = 'http://soprweb.senate.gov/index.cfm?event=processSelectFields'

    jar = cookielib.CookieJar()
    requests.get(FORM_URL, cookies=jar)
    form_page = requests.post(FORM_URL, cookies=jar, data={"searchCriteria":"reportType"})
    d = pq(form_page.text,parser='html')
    reportTypes = map(lambda x: (x.text,x.attrib["value"]),d('select#reportType > option'))
    reportTypes = filter(lambda x: x[1] != "select one", reportTypes)
    reportTypes = dict(reportTypes)
    return reportTypes

def download_house_xml(options):
    FORM_URL = 'http://disclosures.house.gov/ld/LDDownload.aspx?KeepThis=true'

    filing_type_form_map = {
        'Registrations':    {'form': 'LD1', 'quarter': 'ALL'},
        'MidYear':          {'form': 'LD2', 'quarter': 'Q2'},
        'YearEnd':          {'form': 'LD2', 'quarter': 'Q4'},
        '1stQuarter':       {'form': 'LD2', 'quarter': 'Q1'},
        '2ndQuarter':       {'form': 'LD2', 'quarter': 'Q2'},
        '3rdQuarter':       {'form': 'LD2', 'quarter': 'Q3'},
        '4thQuarter':       {'form': 'LD2', 'quarter': 'Q4'},
    }

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    OUT_DIR = os.path.join(CACHE_DIR, 'house_clerk')

    if not os.path.exists(OUT_DIR):
        mkdir_p(OUT_DIR)

    jar = cookielib.CookieJar()
    form_page = requests.get(FORM_URL, cookies=jar)
    d = pq(form_page.text, parser='html')

    form_data = {input.attr('name'): input.val() for input in
                 d('input[name]').items()}

    filing_selector = d('select#selFilesXML')

    space = r'(\ )'
    filing_type = r'(?P<filing_type>(?P<filing_type_year>\d{4})\ (?P<filing_type_form>MidYear|Registrations|YearEnd|(1st|2nd|3rd|4th)Quarter))'
    xml = '(XML)'
    date = r'(\(\ (?P<updated_date>(?P<updated_date_month>\d{1,2})\/(?P<updated_date_day>\d{1,2})\/(?P<updated_date_year>\d{4})))'
    time = r'(?P<updated_time>(?P<updated_time_hour>\d{1,2}):(?P<updated_time_min>\d{2}):(?P<updated_time_sec>\d{2})\ (?P<updated_time_am_pm>PM|AM)\))'

    option_rgx = re.compile(filing_type+space+xml+space+date+space+time)

    dl_options = filing_selector.find('option')

    def _get_response_loc_pair(value):
        try:
            info = re.match(option_rgx, value).groupdict()
        except AttributeError:
            sys.stderr.write(value)
            raise
        fields = dict(form_data, **{filing_selector.attr('name'): value})

        form_type = filing_type_form_map[info['filing_type_form']]
        output_dir = os.path.join(CACHE_DIR,
                                  'house_xml',
                                  form_type['form'],
                                  info['filing_type_year'],
                                  form_type['quarter'])
        if not os.path.exists(output_dir):
            mkdir_p(output_dir)
        output_name = os.path.join(output_dir,
                                   "{year}_{form}_XML.zip".format(
                                       year=info['filing_type_year'],
                                       form=info['filing_type_form']))

        log.info('starting download of {output_loc}'.format(
            output_loc=output_name))

        response = requests.post(FORM_URL, data=fields, stream=True,
                                 cookies=jar)

        return (response, output_name)

    values = [option.attr('value') for option in dl_options.items()]
    # response_loc_pairs = [_get_response_loc_pair(value) for value in values]

    download_all(values, _get_response_loc_pair, options)
