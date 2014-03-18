import os
import logging
from itertools import product

import requests
from stream import ThreadPool
from stream import map, filter

from settings import CACHE_DIR
from .utils import mkdir_p
from .log import set_up_logging


# GENERAL DOWNLOAD FUNCTIONS
def download(url, output_loc):
    request = requests.get(url, stream=True)
    try:
        with open(output_loc, 'wb') as output_file:
            for chunk in request.iter_content():
                output_file.write(chunk)
        return request.headers['content-length']
    except Exception as e:
        if not request.ok:
            request.raise_for_status()
        else:
            raise e


def download_all(url_loc_pairs):
    for url, output_loc in url_loc_pairs:
        yield url, output_loc, download(url, output_loc)


def is_not_cached(url_loc_pair):
    url, output_loc = url_loc_pair
    request = requests.get(url, stream=True)
    if os.path.exists(output_loc):
        downloaded_size = os.path.getsize(output_loc)
        logging.debug(
            'found {output_loc}: {size}'.format(
                output_loc=output_loc,
                size=downloaded_size))
        size_on_server = request.headers['content-length']
        if downloaded_size != size_on_server:
            logging.debug(
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

    log = set_up_logging('download_sopr', loglevel=options.get('loglevel'))

    for url, output_loc, content_length in downloaded:
        log.info(
            'successfully downloaded {url} to {output_loc}({size})'.format(
                url=url, output_loc=output_loc, size=content_length))

    for url, exception in downloaded.failure:
        log.error(
            'downloading from {url} failed: {exception}'.format(
                url=url, exception=exception))
