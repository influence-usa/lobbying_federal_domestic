import os
import logging
from itertools import product

import requests
from stream import ThreadPool
from stream import map, filter

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
    if not response.ok:
        log.warn('response not okay: '+response.reason)
        return False
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
    if options.get('loglevel',None):
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

    downloaded = _urls >> map(_url_to_loc) \
                       >> filter(is_not_cached) \
                       >> ThreadPool(download_all, poolsize=4)

    for url, output_loc, content_length in downloaded:
        log.info(
            'successfully downloaded {url} to {output_loc}({size})'.format(
                url=url, output_loc=output_loc, size=content_length))

    for url, exception in downloaded.failure:
        log.error(
            'downloading from {url} failed: {exception}'.format(
                url=url, exception=exception))
