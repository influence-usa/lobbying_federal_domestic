import json

import pytest
import validictory

from utils.validate import validate_uuid, validate_url


@pytest.fixture
def uuid_fixture():
    data = json.loads(''' {
                            "uuidInt": 117574695023396164616661330147169357159,
                            "uuidHex": "054a4828074e45f293a3a7ffbcd43bfb",
                            "uuidCanon": "054a4828-074e-45f2-93a3-a7ffbcd43bfb"
                        }''')

    schema = {
        "title": "My test schema",
        "properties": {
            "uuidHex": {
                "format": "uuid_hex"
            },
            "uuidInt": {
                "format": "uuid_int"
            },
            "uuidCanon": {
                "format": "uuid_hex"
            }
        }
    }

    return {'data': data, 'schema': schema}


def test_validate_uuid(uuid_fixture):

    uuid_data = uuid_fixture['data']
    uuid_schema = uuid_fixture['schema']

    formatdict = {"uuid_hex": validate_uuid, "uuid_int": validate_uuid}

    # Make sure good data validates
    validictory.validate(uuid_data, uuid_schema, format_validators=formatdict)

    # Make sure bad data doesn't
    with pytest.raises(validictory.ValidationError):
        bad_data = uuid_data.copy()
        bad_data['uuidHex'] = 'not_a_uuid'
        validictory.validate(bad_data, uuid_schema,
                             format_validators=formatdict)


@pytest.fixture
def url_fixture():
    data = json.loads(''' {
                            "test_http": "http://sunlightfoundation.com/api",
                            "test_https": "https://www.aal-usa.com",
                            "test_ftp": "ftp://ftp.fec.gov/FEC/"
                        }''')

    schema = {
        "title": "Url test schema",
        "properties": {
            "test_http": {
                "format": "url_http"
            },
            "test_https": {
                "format": "url_http"
            },
            "test_ftp": {
                "format": "url_ftp"
            },
        }
    }

    return {'data': data, 'schema': schema}


def test_validate_url(url_fixture):

    url_data = url_fixture['data']
    url_schema = url_fixture['schema']

    formatdict = {"url_http": validate_url, "url_ftp": validate_url}

    # Make sure good data validates
    validictory.validate(url_data, url_schema, format_validators=formatdict)

    # Make sure bad data doesn't
    bad_egs = zip(['test_http', 'test_https', 'test_ftp'],
                  ['sunlightfoundation.com', 'https:/www.aal-usa.com',
                   'ftp:://ftp.fec.fgov/FEC/'])
    print bad_egs
    for field, bad_eg in bad_egs:
        with pytest.raises(validictory.ValidationError):
            bad_data = url_data.copy()
            bad_data[field] = bad_eg
            print bad_eg
            validictory.validate(bad_data, url_schema,
                                 format_validators=formatdict)
