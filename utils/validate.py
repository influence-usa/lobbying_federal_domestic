import uuid
import re

import validictory


def validate_uuid(validator, fieldname, value, format_option):

    # print("*********************")
    # print("validator:", validator)
    # print("fieldname:", fieldname)
    # print("value", value)
    # print("format_option", format_option)
    # print("*********************")

    if format_option == "uuid_hex":
        try:
            uuid.UUID(hex=value)
        except Exception as e:
            raise validictory.FieldValidationError("Could not parse UUID from\
                hex string {uuidstr}, reason: {reason}".format(
                uuidstr=value, reason=e), fieldname, value)

    elif format_option == "uuid_int":
        try:
            uuid.UUID(int=value)
        except Exception as e:
            raise validictory.FieldValidationError("Could not parse UUID \
                from int string {uuidstr}, reason: {reason}".format(
                uuidstr=value, reason=e), fieldname, value)
    else:
        raise validictory.FieldValidationError("Invalid format option for \
                'validate_uuid': {fopt}".format(fopt=format_option), fieldname,
                                               value)


def validate_url(validator, fieldname, value, format_option):

    # print("*********************")
    # print("validator:", validator)
    # print("fieldname:", fieldname)
    # print("value", value)
    # print("format_option", format_option)
    # print("*********************")

    # from django.core.validators
    http_regex = re.compile(
        r'^(?:http)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    ftp_regex = re.compile(
        r'^(?:ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if format_option == "url_http":
        if not http_regex.search(value):
            raise validictory.FieldValidationError(
                "String {urlstr} isn't a valid HTTP URL".format(urlstr=value),
                fieldname, value)

    if format_option == "url_ftp":
        if not ftp_regex.search(value):
            raise validictory.FieldValidationError(
                "String {urlstr} isn't a valid FTP URL".format(urlstr=value),
                fieldname, value)


def validate_email(validator, fieldname, value, format_option):

    # print("*********************")
    # print("validator:", validator)
    # print("fieldname:", fieldname)
    # print("value", value)
    # print("format_option", format_option)
    # print("*********************")

    # from django.core.validators
    email_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)  # literal form, ipv4 address (SMTP 4.1.3)

    if not email_regex.search(value):
        raise validictory.FieldValidationError(
            "String {emailstr} isn't a valid email address".format(
                emailstr=value), fieldname, value)
