import os
import logging
import zipfile
from glob import glob

from multiprocessing.dummy import Pool as ThreadPool

from settings import CACHE_DIR, ORIG_DIR
from .utils import mkdir_p, translate_dir
from .log import set_up_logging

log = set_up_logging('extract', loglevel=logging.DEBUG)


def log_result(result):
    if result[0] == 'success':
        src_dir, dest_dir, num_files = result[1:]
        log.info("successfully extracted " +
                 "{src_dir} => {dest_dir} ({num} files)".format(
                     src_dir=src_dir, dest_dir=dest_dir, num=num_files))
    elif result[0] == 'failure':
        loc, e = result[1:]
        log.error("extracting from {loc} failed: {exception}".format(
            loc=loc, exception=str(e)))
    else:
        raise Exception('Result for {loc} was neither success nor failure?')


def check_ext(path, ext=None):
    return os.path.splitext(path)[1] == ext


def extract_zip(cache_path):
    old_path, new_path = translate_dir(cache_path, from_dir=CACHE_DIR,
                                       to_dir=ORIG_DIR)
    try:
        with zipfile.ZipFile(old_path, "r") as z:
            num_files = len(z.namelist())
            z.extractall(new_path)
            return ('success', old_path, new_path, num_files)
    except Exception as e:
        return ('failure', old_path, e)


def extract_all_zips(cache_paths, options):
    threaded = options.get('threaded', False)
    thread_num = options.get('thread_num', 4)

    if threaded:
        pool = ThreadPool(thread_num)
        for path in cache_paths:
            if check_ext(path, ext='.zip'):
                pool.apply_async(extract_zip, args=(path,),
                                 callback=log_result)
            else:
                raise Exception("{} not a zip file!".format(path))
        pool.close()
        pool.join()
    else:
        for path in cache_paths:
            old_path, new_path = translate_dir(path, from_dir=CACHE_DIR,
                                               to_dir=ORIG_DIR)
            log_result(extract_zip(old_path, new_path))


def extract_sopr(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    cache_paths = glob(os.path.join(CACHE_DIR, 'sopr/*/*/*.zip'))
    log.debug("cache paths ({num}):".format(num=len(cache_paths)) +
              "\n\t".join(cache_paths))

    extract_all_zips(cache_paths, options)


def extract_house_xml(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    cache_paths = glob(os.path.join(CACHE_DIR, 'house_xml/*/*/*/*.zip'))
    log.debug("cache paths ({num}):".format(num=len(cache_paths)) +
              "\n\t".join(cache_paths))

    extract_all_zips(cache_paths, options)
