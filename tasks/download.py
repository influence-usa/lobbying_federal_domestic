import os
import sys
import re
import logging
import time
import json
import urlparse
from glob import glob, iglob
from datetime import datetime

from itertools import product
from multiprocessing.dummy import Pool as ThreadPool

import requests

from pyquery import PyQuery as pq
import cookielib
from lxml import etree

from settings import CACHE_DIR, TRANS_DIR
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
        _url = _response.url
        if is_not_cached(_response, _loc):
            try:
                content_length = response_download(_response, _loc)
                return ('success', _url, _loc, content_length)
            except Exception:
                log.warn('{url} something went wrong, trying again ({code} - {reason})'.format(
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
        log.info("starting threaded download")
        pool = ThreadPool(thread_num)
        for val in vals:
            log.debug("async start for {}".format(str(val)))
            pool.apply_async(download, args=(val, get_response_loc_pair),
                             callback=log_result)
        pool.close()
        pool.join()
    else:
        for val in vals:
            log_result(download(val, get_response_loc_pair))


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
def download_sopr_xml(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    def _get_response_loc_pair(url):
        fname = requests.utils.urlparse(url).path.split('/')[-1]
        year, quarter = fname.split('.')[0].split('_')
        output_dir = os.path.join(CACHE_DIR, 'sopr_xml', year, 'Q' + quarter)
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


def download_sopr_field_codes(field_name, options):
    FORM_URL = 'http://soprweb.senate.gov/index.cfm?event=processSelectFields'

    jar = cookielib.CookieJar()
    requests.get(FORM_URL, cookies=jar)
    form_page = requests.post(FORM_URL, cookies=jar,
                              data={"searchCriteria": field_name})
    d = pq(form_page.text, parser='html')
    field_code_map = {x.text: x.attrib["value"] for x in
                      d('select#{} > option'.format(field_name))
                      if x.text != "select one"}
    return field_code_map


def download_sopr_html(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    _base_url = 'http://soprweb.senate.gov/index.cfm'
    _search_url_rgx = re.compile(r"(window\.open\(')(.*?)('\))", re.IGNORECASE)
    _report_types = download_sopr_field_codes('reportType', options)
    _report_type_reverse = {v: k for k, v in _report_types.iteritems()}

    _filing_type_to_subyear = {
        "FIRST QUARTER (NO ACTIVITY)": "Q1",
        "FIRST QUARTER AMENDMENT (NO ACTIVITY)": "Q1",
        "FIRST QUARTER AMENDMENT": "Q1",
        "FIRST QUARTER REPORT": "Q1",
        "FIRST QUARTER TERMINATION (NO ACTIVITY)": "Q1",
        "FIRST QUARTER TERMINATION AMENDMENT (NO ACTIVITY)": "Q1",
        "FIRST QUARTER TERMINATION AMENDMENT": "Q1",
        "FIRST QUARTER TERMINATION": "Q1",
        "FOURTH QUARTER (NO ACTIVITY)": "Q4",
        "FOURTH QUARTER AMENDMENT (NO ACTIVITY)": "Q4",
        "FOURTH QUARTER AMENDMENT": "Q4",
        "FOURTH QUARTER REPORT": "Q4",
        "FOURTH QUARTER TERMINATION (NO ACTIVITY)": "Q4",
        "FOURTH QUARTER TERMINATION AMENDMENT (NO ACTIVITY)": "Q4",
        "FOURTH QUARTER TERMINATION AMENDMENT": "Q4",
        "FOURTH QUARTER TERMINATION": "Q4",
        "MID-YEAR (NO ACTIVITY)": "Q2",
        "MID-YEAR AMENDMENT (NO ACTIVITY)": "Q2",
        "MID-YEAR AMENDMENT": "Q2",
        "MID-YEAR REPORT": "Q2",
        "MID-YEAR REPORT": "Q2",
        "MID-YEAR TERMINATION (NO ACTIVITY)": "Q2",
        "MID-YEAR TERMINATION AMENDMENT (NO ACTIVITY)": "Q2",
        "MID-YEAR TERMINATION AMENDMENT": "Q2",
        "MID-YEAR TERMINATION LETTER": "Q2",
        "MID-YEAR TERMINATION": "Q2",
        "MISC TERM": "MISC",
        "MISC. DOC": "MISC",
        "REGISTRATION AMENDMENT": "REG",
        "REGISTRATION": "REG",
        "SECOND QUARTER (NO ACTIVITY)": "Q2",
        "SECOND QUARTER AMENDMENT (NO ACTIVITY)": "Q2",
        "SECOND QUARTER AMENDMENT": "Q2",
        "SECOND QUARTER REPORT": "Q2",
        "SECOND QUARTER TERMINATION (NO ACTIVITY)": "Q2",
        "SECOND QUARTER TERMINATION AMENDMENT (NO ACTIVITY)": "Q2",
        "SECOND QUARTER TERMINATION AMENDMENT": "Q2",
        "SECOND QUARTER TERMINATION": "Q2",
        "THIRD QUARTER (NO ACTIVITY)": "Q3",
        "THIRD QUARTER AMENDMENT (NO ACTIVITY)": "Q3",
        "THIRD QUARTER AMENDMENT": "Q3",
        "THIRD QUARTER REPORT": "Q3",
        "THIRD QUARTER TERMINATION (NO ACTIVITY)": "Q3",
        "THIRD QUARTER TERMINATION AMENDMENT (NO ACTIVITY)": "Q3",
        "THIRD QUARTER TERMINATION AMENDMENT": "Q3",
        "THIRD QUARTER TERMINATION": "Q3",
        "YEAR-END (NO ACTIVITY)": "Q4",
        "YEAR-END AMENDMENT (NO ACTIVITY)": "Q4",
        "YEAR-END AMENDMENT": "Q4",
        "YEAR-END REPORT": "Q4",
        "YEAR-END TERMINATION (NO ACTIVITY)": "Q4",
        "YEAR-END TERMINATION AMENDMENT (NO ACTIVITY)": "Q4",
        "YEAR-END TERMINATION AMENDMENT": "Q4",
        "YEAR-END TERMINATION LETTER": "Q4",
        "YEAR-END TERMINATION": "Q4",
    }

    def _parse_search_result(result):
        filing_type = result.xpath('td[3]')[0].text
        filing_year = result.xpath('td[6]')[0].text
        try:
            m = re.match(_search_url_rgx, result.attrib['onclick'])
        except KeyError:
            log.error('element {} has no onclick attribute'.format(
                      etree.tostring(result)))
        _doc_path = m.groups()[1]
        _params = dict(urlparse.parse_qsl(urlparse.urlparse(_doc_path).query))
        _params['Type'] = filing_type
        _params['Year'] = filing_year
        return _params

    def _get_newest_filings(cut_field, cut_vals, since=datetime.today()):
        all_params = []
        start = datetime.strftime(since, '%m/%d/%Y')
        end = datetime.strftime(datetime.today(), '%m/%d/%Y')
        search_params = {'event': 'processSearchCriteria'}
        search_form = {'datePostedStart': start,
                       'datePostedEnd': end}
        for cut_val in cut_vals:
            search_form.update({cut_field: cut_val})
            resp = requests.post(_base_url, params=search_params,
                                 data=search_form)
            d = pq(resp.text, parser='html')
            results = d('tbody tr')
            if len(results) >= 3000:
                error_msg = "More than 3000 results for params:\n{}".format(
                            json.dumps(search_params, indent=2))
                raise Exception(error_msg)
            for result in results:
                params = _parse_search_result(result)
                if params:
                    all_params.append(params)
                else:
                    log.error('unable to parse {}'.format(
                              etree.tostring(result)))
        return all_params

    def _build_params_from_xml_json(xml_json_loc):
        params = {}
        with open(xml_json_loc) as xml_json_file:
            json_dict = json.load(xml_json_file)
            params['event'] = 'getFilingDetails'
            params['filingID'] = json_dict['ID'].lower()

            # Get relevant fields from json
            for field in ['Type', 'Year']:
                try:
                    params[field] = json_dict[field]
                except KeyError:
                    log.error(
                        '{f_loc} missing required field {fieldname}!'.format(
                            f_loc=xml_json_loc, fieldname=field))
                    return False

            # Look up type in our mapping
            try:
                filing_type_id = _report_types[params['Type']]
            except KeyError:
                log.error('{f_loc} unknown Type: {filingtype}'.format(
                    f_loc=xml_json_loc, filingtype=params['Type']))
                return False

            params['filingTypeID'] = filing_type_id

        return params

    def _get_response_loc_pair(params):
        _params = params.copy()
        filing_year = _params.pop('Year', None)
        filing_type = _params.pop('Type', None)
        output_fname = '.'.join([_params['filingID'], 'html'])
        response = requests.get(_base_url, params=_params)
        subyear = _filing_type_to_subyear[filing_type]
        output_dir = os.path.join(CACHE_DIR,
                                  'sopr_html',
                                  filing_year,
                                  subyear)
        if not os.path.exists(output_dir):
            log.debug("making {}".format(output_dir))
            mkdir_p(output_dir)
        output_loc = os.path.join(output_dir, output_fname)
        return (response, output_loc)

    if options.get('backfill', None):
        log.debug('globbing up archived json')
        xml_json_files = glob(os.path.join(
                              TRANS_DIR, 'sopr_xml', '*', '*', '*.json'))
        log.debug('building params')
        all_params = []
        for loc in xml_json_files:
            params = _build_params_from_xml_json(loc)
            if params:
                all_params.append(params)
    else:
        state_map = download_sopr_field_codes('clientState', None)
        all_params = _get_newest_filings('clientState', state_map.values())

    log.info('beginning {num_vals} downloads'.format(num_vals=len(all_params)))
    download_all(all_params, _get_response_loc_pair, options)


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

    _space = r'(\ )'
    _filing_type = r'(?P<filing_type>(?P<filing_type_year>\d{4})\ (?P<filing_type_form>MidYear|Registrations|YearEnd|(1st|2nd|3rd|4th)Quarter))'
    _xml = '(XML)'
    _date = r'(\(\ (?P<updated_date>(?P<updated_date_month>\d{1,2})\/(?P<updated_date_day>\d{1,2})\/(?P<updated_date_year>\d{4})))'
    _time = r'(?P<updated_time>(?P<updated_time_hour>\d{1,2}):(?P<updated_time_min>\d{2}):(?P<updated_time_sec>\d{2})\ (?P<updated_time_am_pm>PM|AM)\))'

    option_rgx = re.compile(_filing_type +
                            _space +
                            _xml +
                            _space +
                            _date +
                            _space +
                            _time)

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
