import logging
import logging.handlers
import os.path

import settings

from .utils import mkdir_p


class EncodingFormatter(logging.Formatter):

    def __init__(self, fmt, datefmt=None, encoding=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding = encoding

    def format(self, record):
        result = logging.Formatter.format(self, record)
        if isinstance(result, unicode):
            result = result.encode(self.encoding or 'utf-8')
        return result


def set_up_logging(function_name, loglevel):
    format_string = ' - '.join(["%(asctime)s",
                               "%(name)s",
                               "%(funcName)s",
                               "%(levelname)s",
                               "%(message)s"])
    # create logger
    log = logging.getLogger(function_name)
    log.setLevel(loglevel)
    formatter = logging.Formatter(format_string)
    
    # make sure log dir exists
    if not os.path.exists(settings.LOG_DIR):
       mkdir_p(settings.LOG_DIR) 

    # always create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    log.addHandler(console_handler)

    # create file handler and set level to loglevel
    file_handler = logging.FileHandler(os.path.join(settings.LOG_DIR,
                                                    function_name + '.log'))
    file_handler.setLevel(loglevel)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    # create email handler and set level to warn
    if settings.LOGGING_EMAIL:
        eh = logging.handlers.SMTPHandler(
            (settings.LOGGING_EMAIL['hostname'],
             settings.LOGGING_EMAIL['port']),     # host, port tuple
            settings.LOGGING_EMAIL['from'],       # from address
            settings.LOGGING_EMAIL['to'],         # to addresses
            settings.LOGGING_EMAIL['subject'],    # email subject
            (settings.LOGGING_EMAIL['user_name'],
             settings.LOGGING_EMAIL['password'])  # credentials tuple
        )
        eh.setLevel(loglevel)
        eh.setFormatter(formatter)
        eh.setFormatter(EncodingFormatter('%(message)s', encoding='iso8859-1'))
        log.addHandler(eh)

    return log
