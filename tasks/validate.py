import json
import os
import logging
from glob import iglob
from multiprocessing import Pool as ThreadPool

import validictory
from validictory import SchemaValidator

from schema.validate.sopr_html import transformed_ld1_schema,\
    transformed_ld2_schema
from utils.validate import validate_uuid, validate_url, validate_email
from utils import set_up_logging
from settings import TRANS_DIR

format_validators = {"uuid_hex": validate_uuid,
                     "url_http": validate_url,
                     "email": validate_email}

log = set_up_logging('validate', loglevel=logging.DEBUG)

required_by_default = True

blank_by_default = False

disallow_unknown_properties = True

apply_default_to_data = False

validator = SchemaValidator(format_validators, required_by_default,
                            blank_by_default, disallow_unknown_properties,
                            apply_default_to_data)


def log_result(result):
    if result[0] == 'valid':
        loc = result[1]
        log.debug("valid - {fname}".format(fname=loc))
    elif result[0] == 'invalid':
        loc, fieldname, value, message = result[1:]
        log.error("invalid - {loc}\n\t**field_info**{field}: {value}\n\t**message**{msg}".format(
            loc=loc, field=fieldname, value=value, msg=message))


def validate_one(loc, schema):
    with open(loc, 'r') as json_file:
        data = json.load(json_file)
        try:
            validator.validate(data, schema)
            return ('valid', loc)
        except validictory.ValidationError as e:
            msg = e.message.split("errorlist = ")[-1]
            return ('invalid', loc, e.fieldname, e.value, msg)


def validate_all(locs, schema, options):
    threaded = options.get('threaded', False)
    thread_num = options.get('thread_num', 4)

    if threaded:
        pool = ThreadPool(thread_num)
        for loc in locs:
            pool.apply_async(validate_one, args=(loc, schema),
                             callback=log_result)
        pool.close()
        pool.join()
    else:
        for loc in locs:
            log_result(validate_one(loc, schema))


def validate_sopr_html(options):
    if options.get('loglevel', None):
        log.setLevel(options['loglevel'])

    ld1_locs = iglob(os.path.join(TRANS_DIR, 'sopr_html', '*', 'REG', '*.json'))
    log.info("beginning LD-1 validation")
    validate_all(ld1_locs, transformed_ld1_schema, options)
    log.info("finished LD-1 validation")

    ld2_locs = iglob(os.path.join(TRANS_DIR, 'sopr_html', '*', 'Q[1-4]', '*.json'))
    log.info("beginning LD-2 validation")
    validate_all(ld2_locs, transformed_ld2_schema, options)
    log.info("finished LD-2 validation")
