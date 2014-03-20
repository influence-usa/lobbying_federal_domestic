import os

# read in an opt-in config file for changing directories and supplying email settings
# returns None if it's not there, and this should always be handled gracefully
path = "config.yml"
if os.path.exists(path):
  # Don't use a cached config file, just in case, and direct_yaml_load is not yet defined.
  import yaml
  config = yaml.load(open(path))
else:
  config = None

basedir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'data')

if not config:
    LOG_DIR = os.path.join(basedir,'log')
    LOGGING_EMAIL = None
    TRANS_DIR = os.path.join(basedir,'transformed')
    CACHE_DIR = os.path.join(basedir,'cache')
    ORIG_DIR = os.path.join(basedir,'original')
else:
    LOG_DIR = os.path.realpath(config.log)
    LOGGING_EMAIL = config.email
    DATA_DIR = os.path.realpath(config.output.data)
    CACHE_DIR = os.path.realpath(config.output.cache)
    ORIG_DIR = os.path.realpath(config.output.original)
