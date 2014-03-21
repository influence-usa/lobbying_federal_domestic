import os
import re
import logging
from itertools import product

import requests
# Importing from stream.py, but renaming to avoid confusion with built-ins
from stream import ThreadPool
from stream import map as st_map
from stream import filter as st_filter

from settings import CACHE_DIR
from .utils import mkdir_p
from .log import set_up_logging

log = set_up_logging('download', loglevel=logging.DEBUG)


# GENERAL DOWNLOAD FUNCTIONS
def download(url, output_loc):
    response = requests.get(url, stream=True)
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


def download_all(url_loc_pairs):
    for url, output_loc in url_loc_pairs:
        yield url, output_loc, download(url, output_loc)


def is_not_cached(url_loc_pair):
    url, output_loc = url_loc_pair
    response = requests.get(url, stream=True)
    if os.path.exists(output_loc):
        downloaded_size = int(os.path.getsize(output_loc))
        log.debug(
            'found {output_loc}: {size}'.format(
                output_loc=output_loc,
                size=downloaded_size))
        size_on_server = int(response.headers['content-length'])
        if downloaded_size != size_on_server:
            log.debug(
                're-downloaded {url}: {size}'.format(
                    url=url,
                    size=size_on_server))
            return True
        else:
            return False
    else:
        return True


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
    from selenium import webdriver

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    OUT_DIR = os.path.join(CACHE_DIR, 'house_clerk')

    if not os.path.exists(OUT_DIR):
        mkdir_p(OUT_DIR)

    def _go_to_url(driver, url):
        driver.get(search_url)

    # ### Firefox profile for auto-downloading
    fp = webdriver.FirefoxProfile()

    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", OUT_DIR)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                      "application/x-octet-stream")

    driver = webdriver.Firefox(firefox_profile=fp)

    search_url = "http://disclosures.house.gov/ld/ldsearch.aspx"

    _go_to_url(driver, search_url)
    dl_button = driver.find_element_by_css_selector(
                 'html body div#search_container div#downloadLink p a')
    dl_button.click()

    driver.switch_to_frame('TB_iframeContent')

    filing_selector = driver.find_element_by_css_selector('select#selFilesXML')

    space = r'(\ )'
    filing_type = r'(?P<filing_type>(?P<filing_type_year>\d{4})\ (?P<filing_type_form>MidYear|Registrations|YearEnd|(1st|2nd|3rd|4th)Quarter))'
    xml = '(XML)'
    date = r'(\(\ (?P<updated_date>(?P<updated_date_day>\d{1,2})\/(?P<updated_date_month>\d{2})\/(?P<updated_date_year>\d{4})))'
    time = r'(?P<updated_time>(?P<updated_time_hour>\d{1,2}):(?P<updated_time_min>\d{2}):(?P<updated_time_sec>\d{2})\ (?P<updated_time_am_pm>PM|AM)\))'

    option_rgx = re.compile(filing_type+space+xml+space+date+space+time)

    dl_options = filing_selector.find_elements_by_tag_name('option')

    dl_options_with_metadata = zip(dl_options, (re.match(option_rgx,
                                   o.get_attribute('value')).groupdict()
                                   for o in dl_options))

    for option, metadata in dl_options_with_metadata:
        option.click()
        driver.find_element_by_css_selector('#btnDownloadXML').click()

    driver.close()
