import os
import re
import logging
from itertools import product

import requests
# Importing from stream.py, but renaming to avoid confusion with built-ins
from stream import ThreadPool, Stream
from stream import map as st_map
from stream import filter as st_filter

from pyquery import PyQuery as pq
import cookielib
import traceback

from settings import CACHE_DIR
from .utils import mkdir_p
from .log import set_up_logging

log = set_up_logging('download', loglevel=logging.DEBUG)


# GENERAL DOWNLOAD FUNCTIONS
def response_download(response_loc_pair):
    response, output_loc = response_loc_pair
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
        response.raise_for_status()

def download(url, output_loc):
    return response_download((requests.get(url, stream=True), output_loc))


def download_all(url_loc_pairs):
    for url, output_loc in url_loc_pairs:
        yield url, output_loc, download(url, output_loc)

def response_is_not_cached(response_loc_pair):
    response, output_loc = response_loc_pair
    if os.path.exists(output_loc):
        downloaded_size = int(os.path.getsize(output_loc))
        log.debug(
            'found {output_loc}: {size}'.format(
                output_loc=output_loc,
                size=downloaded_size))
        size_on_server = int(response.headers['content-length'])
        if downloaded_size != size_on_server:
            log.debug(
                're-downloaded {output_loc}: {size}'.format(
                    output_loc=output_loc,
                    size=size_on_server))
            return True
        else:
            response.close()
            return False
    else:
        return True

def is_not_cached(url_loc_pair):
    url, output_loc = url_loc_pair
    response = requests.head(url)
    return response_is_not_cached((response, output_loc))

# SPECIFIC TASKS
def download_sopr(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    def _url_to_loc(url):
        fname = requests.utils.urlparse(url).path.split('/')[-1]
        year, quarter = fname.split('.')[0].split('_')
        output_dir = os.path.join(CACHE_DIR, 'sopr', year, 'Q' + quarter)
        if not os.path.exists(output_dir):
            mkdir_p(output_dir)
        output_loc = os.path.join(output_dir, fname)
        return (url, output_loc)

    _url_template = 'http://soprweb.senate.gov/downloads/{year}_{quarter}.zip'

    _urls = [_url_template.format(year=year, quarter=quarter)
             for year, quarter in
             product(xrange(1999, 2015), xrange(1, 5))]

    downloaded = _urls >> st_map(_url_to_loc) \
                       >> st_filter(is_not_cached) \
                       >> ThreadPool(download_all, poolsize=4)

    for url, output_loc, content_length in downloaded:
        log.info(
            'successfully downloaded {url} to {output_loc}({size})'.format(
                url=url, output_loc=output_loc, size=content_length))

    for url, exception in downloaded.failure:
        log.error(
            'downloading from {url} failed: {exception}'.format(
                url=url, exception=exception))


def download_house_xml(options):
    FORM_URL = 'http://disclosures.house.gov/ld/LDDownload.aspx?KeepThis=true'

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    OUT_DIR = os.path.join(CACHE_DIR, 'house_clerk')

    if not os.path.exists(OUT_DIR):
        mkdir_p(OUT_DIR)

    jar = cookielib.CookieJar()
    form_page = requests.get(FORM_URL, cookies=jar)
    d = pq(form_page.text, parser='html')

    form_data = {input.attr('name'): input.val() for input in d('input[name]').items()}

    filing_selector = d('select#selFilesXML')

    space = r'(\ )'
    filing_type = r'(?P<filing_type>(?P<filing_type_year>\d{4})\ (?P<filing_type_form>MidYear|Registrations|YearEnd|(1st|2nd|3rd|4th)Quarter))'
    xml = '(XML)'
    date = r'(\(\ (?P<updated_date>(?P<updated_date_day>\d{1,2})\/(?P<updated_date_month>\d{2})\/(?P<updated_date_year>\d{4})))'
    time = r'(?P<updated_time>(?P<updated_time_hour>\d{1,2}):(?P<updated_time_min>\d{2}):(?P<updated_time_sec>\d{2})\ (?P<updated_time_am_pm>PM|AM)\))'

    option_rgx = re.compile(filing_type+space+xml+space+date+space+time)

    dl_options = filing_selector.find('option')

    def _get_request_loc_pair(value):
        info = re.match(option_rgx, value).groupdict()
        fields = dict(form_data, **{filing_selector.attr('name'): value})

        output_dir = os.path.join(CACHE_DIR, 'house_clerk')
        mkdir_p(output_dir)
        output_name = os.path.join(output_dir, "%s_%s_XML.zip" % (info['filing_type_year'], info['filing_type_form']))

        log.info('starting download of {output_loc}'.format(output_loc=output_name))

        response = requests.post(FORM_URL, data=fields, stream=True, cookies=jar)

        return (response, output_name)

    def _download_all(q):
        for result in q:
            yield result[1], response_download(result)

    downloaded = \
        (option.attr('value') for option in dl_options.items()) \
        >> st_map(_get_request_loc_pair) \
        >> st_filter(response_is_not_cached) \
        >> ThreadPool(_download_all, poolsize=4)

    for output_loc, content_length in downloaded:
        log.info(
            'successfully downloaded to {output_loc}({size})'.format(
                output_loc=output_loc, size=content_length))

    for (response, output_loc), exception in downloaded.failure:
        log.error(
            'downloading to {output_loc} failed: {exception}'.format(
                output_loc=output_loc, exception=exception))