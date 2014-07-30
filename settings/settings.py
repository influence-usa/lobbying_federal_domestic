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

basedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
DATA_DIR = os.path.join(basedir, 'data')
TEST_DATA_DIR = os.path.join(basedir, 'test_data')

if not config:
    LOG_DIR = os.path.join(basedir, 'log')
    LOGGING_EMAIL = None
    TRANS_DIR = os.path.join(DATA_DIR, 'transformed')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')
    ORIG_DIR = os.path.join(DATA_DIR, 'original')
    TEST_TRANS_DIR = os.path.join(TEST_DATA_DIR, 'transformed')
    TEST_CACHE_DIR = os.path.join(TEST_DATA_DIR, 'cache')
    TEST_ORIG_DIR = os.path.join(TEST_DATA_DIR, 'original')
    TEST_ORIG_TARGET_DIR = os.path.join(TEST_DATA_DIR, 'original_target')
    TEST_TRANS_TARGET_DIR = os.path.join(TEST_DATA_DIR, 'transformed_target')
else:
    LOG_DIR = os.path.realpath(config.log)
    LOGGING_EMAIL = config.email
    DATA_DIR = os.path.realpath(config.output.data)
    CACHE_DIR = os.path.realpath(config.output.cache)
    ORIG_DIR = os.path.realpath(config.output.original)
    TEST_DATA_DIR = os.path.realpath(config.test.data)
    TEST_CACHE_DIR = os.path.realpath(config.test.cache)
    TEST_ORIG_DIR = os.path.realpath(config.test.original)
