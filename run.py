#!/usr/bin/env python

import sys
import logging
import argparse


import tasks


loglevels = {'info': logging.INFO,
             'debug': logging.DEBUG,
             'error': logging.ERROR,
             'warn': logging.WARN}

possible_actions = ['download', 'extract', 'transform', 'validate']
data_types = ['sopr_html', 'sopr_xml', 'house_xml', 'sopr_report_types']

parser = argparse.ArgumentParser(description='Run scripts')

parser.add_argument('action', choices=possible_actions)
parser.add_argument('data_type', choices=data_types)
parser.add_argument('--force', action='store_true')
parser.add_argument('--threaded', action='store_true')
parser.add_argument('--backfill', action='store_true')
parser.add_argument('--thread_num', action='store', type=int)
parser.add_argument('--loglevel', default='debug')

options = parser.parse_args().__dict__
options['loglevel'] = loglevels[options['loglevel']]

try:
    task_mod = getattr(tasks, '{action}_{data_type}'.format(**options))
except AttributeError:
    "Not implemented yet, sorry!"
finally:
    task_mod(options)
