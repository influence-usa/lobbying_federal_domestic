#!/usr/bin/env python

import sys
import logging
import argparse
from importlib import import_module

import tasks

loglevels = {'info': logging.INFO,
             'debug': logging.DEBUG,
             'error': logging.ERROR,
             'warn': logging.WARN}

possible_actions = ['download', 'extract']
data_types = ['sopr', ]

parser = argparse.ArgumentParser(description='Run scripts')

parser.add_argument('action', choices=possible_actions)
parser.add_argument('data_type', choices=data_types)
parser.add_argument('--force', action='store_true')
parser.add_argument('--loglevel', default='debug')

options = parser.parse_args().__dict__
options['loglevel'] = loglevels[options['loglevel']]

task_mod = getattr(tasks, '{action}_{data_type}'.format(**options))
task_mod(options)
