import os
import shutil
import logging
import zipfile
import json
from collections import defaultdict
from glob import glob

from multiprocessing.dummy import Pool as ThreadPool

from lxml import etree

from settings import CACHE_DIR, ORIG_DIR, TEST_CACHE_DIR, TEST_ORIG_DIR
from .utils import mkdir_p, translate_dir
from .log import set_up_logging
from .schema import ld1_schema, ld2_schema

log = set_up_logging('extract', loglevel=logging.DEBUG)

html_parser = etree.HTMLParser()


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


def apply_element_node(parsed, node):
    _parse_fct = node['parser']
    _path = node['path']
    try:
        # log.debug(_path)
        element = parsed.xpath(_path)[0]
        return _parse_fct(element)
    except IndexError:
        # log.debug(parsed.xpath(_path))
        return None


def apply_container_node(parsed, node):
    _parse_fct = node['parser']
    _children = node['children']
    _path = node['path']
    element_array = parsed.xpath(_path)
    if element_array:
        return [r for r in _parse_fct(element_array, _children) if any(r.values())]
    else:
        return []


def extract_html(cache_path, schema_elements, schema_containers, cache_dir, orig_dir):
    old_path, new_path = translate_dir(cache_path, from_dir=cache_dir,
                                       to_dir=orig_dir)
    filename = os.path.basename(old_path).split(os.extsep)[0]
    new_path = os.extsep.join([os.path.join(new_path, filename), 'json'])
    # log.info('old: '+old_path)
    # log.info('new: '+new_path)
    record = defaultdict(dict)
    record['document_id'] = filename
    try:
        with open(old_path, "r") as html:
            _parsed = etree.parse(html, html_parser)
            # print etree.tostring(_parsed)
            for node in schema_elements:
                _section = node['section']
                _field = node['field']
                record[_section][_field] = apply_element_node(_parsed, node)
            for node in schema_containers:
                _section = node['section']
                _field = node['field']
                record[_section][_field] = apply_container_node(_parsed, node)
            json.dump(record, open(new_path, 'w'))
            return ('success', old_path, new_path, 1)
    except Exception as e:
        return ('failure', old_path, e)


def copy_cached_files(cache_paths, options):
    for cache_path in cache_paths:
        old_path, new_path = translate_dir(cache_path, from_dir=CACHE_DIR,
                                           to_dir=ORIG_DIR)
        shutil.move(old_path, new_path)


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
            log_result(extract_zip(path))


def extract_all_html(cache_paths, schema_elements, schema_containers, options):
    threaded = options.get('threaded', False)
    thread_num = options.get('thread_num', 4)
    if options.get('test', False):
        cache_dir = TEST_CACHE_DIR
        orig_dir = TEST_ORIG_DIR
    else:
        cache_dir = CACHE_DIR
        orig_dir = ORIG_DIR

    if threaded:
        pool = ThreadPool(thread_num)
        for path in cache_paths:
            if check_ext(path, ext='.html'):
                pool.apply_async(extract_html, args=(path, schema_elements,
                                 schema_containers, cache_dir, orig_dir), 
                                 callback=log_result)
            else:
                raise Exception("{} not an html file!".format(path))
        pool.close()
        pool.join()
    else:
        for path in cache_paths:
            log_result(extract_html(path, schema_elements, schema_containers,
                                    cache_dir, orig_dir))


def extract_sopr_xml(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    cache_paths = glob(os.path.join(CACHE_DIR, 'sopr_xml/*/*/*.zip'))
    log.debug("cache paths ({num}):".format(num=len(cache_paths)) +
              "\n\t".join(cache_paths))

    extract_all_zips(cache_paths, options)


def extract_sopr_html(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    # ld1_cache_paths = glob(os.path.join(CACHE_DIR, 'sopr_html/*/REG/*.html'))
    ld1_cache_paths = glob(os.path.join(CACHE_DIR, 'sopr_html/200[89]/REG/*.html')) + \
        glob(os.path.join(CACHE_DIR, 'sopr_html/201[0-9]/REG/*.html'))
    log.debug("cache paths ({num}):".format(num=len(ld1_cache_paths)) +
              "\n\t".join(ld1_cache_paths))

    ld1_containers = filter(lambda x: 'children' in x, ld1_schema)
    ld1_elements = filter(lambda x: 'children' not in x, ld1_schema)
    extract_all_html(ld1_cache_paths, ld1_elements, ld1_containers, options)

    ld2_cache_paths = glob(os.path.join(CACHE_DIR,
                           'sopr_html/*/Q[1-4]/*.html'))
    ld2_cache_paths = glob(os.path.join(CACHE_DIR, 'sopr_html/200[89]/Q[1-4]/*.html')) + \
        glob(os.path.join(CACHE_DIR, 'sopr_html/201[0-9]/Q[1-4]/*.html'))
    ld2_containers = filter(lambda x: 'children' in x, ld2_schema)
    ld2_elements = filter(lambda x: 'children' not in x, ld2_schema)
    extract_all_html(ld2_cache_paths, ld2_elements, ld2_containers, options)


def extract_house_xml(options):
    if not os.path.exists(ORIG_DIR):
        mkdir_p(ORIG_DIR)

    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    cache_paths = glob(os.path.join(CACHE_DIR, 'house_xml/*/*/*/*.zip'))
    log.debug("cache paths ({num}):".format(num=len(cache_paths)) +
              "\n\t".join(cache_paths))

    extract_all_zips(cache_paths, options)
