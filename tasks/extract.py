import os
import logging
import zipfile
from glob import glob

from stream import ThreadPool
from stream import map, filter

from settings import CACHE_DIR, ORIG_DIR
from .utils import mkdir_p, translate_dir
from .log import set_up_logging

log = set_up_logging('extract', loglevel=logging.DEBUG)


def check_ext(path, ext=None):
    return os.path.splitext(path)[1] == ext


def extract_zip(path, destination_dir):
    with zipfile.ZipFile(path, "r") as z:
        num_files = len(z.namelist())
        z.extractall(destination_dir)
        return (path, destination_dir, num_files)


def extract_all_zips(path_dest_pairs):
    for path, destination_dir in path_dest_pairs:
        yield extract_zip(path, destination_dir)


def extract_sopr(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    cache_paths = glob(os.path.join(CACHE_DIR, 'sopr/*/*/*.zip'))
    log.debug("cache paths ({num}):".format(num=len(cache_paths)) +
              "\n\t".join(cache_paths))

    extracted = cache_paths >> filter(lambda x: check_ext(x, ext='.zip')) \
                            >> map(lambda p: translate_dir(p,
                                                           from_dir=CACHE_DIR,
                                                           to_dir=ORIG_DIR)) \
                            >> ThreadPool(extract_all_zips)

    for path, destination_dir, num_files in extracted:
        log.info("successfully extracted " +
                 "{path} to {dest_dir} ({num} files)".format(
                    path=path, dest_dir=destination_dir, num=num_files))

    for url, exception in extracted.failure:
        log.error("extracting from {path} failed: {exception}".format(
            path=url, exception=exception))
