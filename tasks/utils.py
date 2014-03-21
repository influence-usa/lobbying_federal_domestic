import os, os.path, errno, sys, traceback, zipfile
import re, htmlentitydefs
import json
from pytz import timezone
import datetime, time
from lxml import html, etree
import scrapelib
import pprint
import logging

import smtplib
import email.utils
from email.mime.text import MIMEText
import getpass


# read in an opt-in config file for changing directories and supplying email settings
# returns None if it's not there, and this should always be handled gracefully
path = "config.yml"
if os.path.exists(path):
  # Don't use a cached config file, just in case, and direct_yaml_load is not yet defined.
  import yaml
  config = yaml.load(open(path))
else:
  config = None


eastern_time_zone = timezone('US/Eastern')

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc: # Python >2.5
    if exc.errno == errno.EEXIST:
      pass
    else:
      raise

def translate_dir(path, from_dir=None, to_dir=None):
    destination_dir = os.path.dirname(path.replace(from_dir, to_dir))
    if not os.path.exists(destination_dir):
        mkdir_p(destination_dir)
    return (path, destination_dir)

