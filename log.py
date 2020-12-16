#!/usr/bin/env python
# -*- encoding=utf8 -*-
import logging
import logging.handlers
import textwrap
from datetime import datetime

now = datetime.now()
datetimeStr = now.strftime('%Y-%m-%d %H-%M-%S')

LOG_FILENAME = './log/{}-jd-assistant.log'.format(datetimeStr)
REQUEST_LOG = './log/{}-jd-assistant-request.log'.format(datetimeStr)
REQUEST_LOG_DETAIL = './log/{}-jd-assistant-request-detail.log'.format(datetimeStr)

logger = logging.getLogger()
http_logger = logging.getLogger("http_logger")
http_request_url_cookies_logger = logging.getLogger("http_request_url_cookies_logger")


class HttpFormatter(logging.Formatter):

    def _formatHeaders(self, d):
        return '\n'.join(f'{k}: {v}' for k, v in d.items())

    def _formatHeadersCookies(self, d):
        return 'Cookie: ' + d.get('Cookie', 'parser not found')

    def formatMessage(self, record):
        result = super().formatMessage(record)
        if record.name == 'http_logger':
            result += textwrap.dedent('''
                ---------------- req  >>>>>>>
                {req.method} {req.url}
                {reqhdrs}

                {req.body}
                ---------------- resp <<<<<<<
                {res.status_code} {res.reason} {res.url}
                {reshdrs}

                {res.text}
            ''').format(
                req=record.req,
                res=record.res,
                reqhdrs=self._formatHeaders(record.req.headers),
                reshdrs=self._formatHeaders(record.res.headers),
            )
        if record.name == 'http_request_url_cookies_logger':
            result += textwrap.dedent('''
                {req.method} {req.url}
                {cookies}
            ''').format(
                req=record.req,
                cookies=self._formatHeadersCookies(record.req.headers),
            )

        return result


def set_logger():
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('{asctime} [{levelname}] t-{thread} {name} {filename}:{lineno} - {message}', style='{')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def set_http_logger():
    http_logger.setLevel(logging.DEBUG)
    formatter = HttpFormatter('{asctime} [{levelname}] t-{thread} {name} {filename}:{lineno} - {message}', style='{')

    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(formatter)
    # http_logger.addHandler(console_handler)

    file1_handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file1_handler.setFormatter(formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        REQUEST_LOG_DETAIL, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    http_logger.addHandler(file1_handler)
    http_logger.addHandler(file_handler)


def set_http_request_url_cookies_logger():
    http_request_url_cookies_logger.setLevel(logging.DEBUG)
    formatter = HttpFormatter('{asctime} t-{thread} - {message}', style='{')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    http_request_url_cookies_logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        REQUEST_LOG, maxBytes=10485760, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    http_request_url_cookies_logger.addHandler(file_handler)


set_logger()
set_http_logger()
set_http_request_url_cookies_logger()
