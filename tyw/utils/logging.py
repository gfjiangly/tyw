# coding: utf8

"""Utilities for logging."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from email.mime.text import MIMEText
import logging
import smtplib
import sys


def send_email(subject, body, to):
    s = smtplib.SMTP('localhost')
    mime = MIMEText(body)
    mime['Subject'] = subject
    mime['To'] = to
    s.sendmail('detectron', to, mime.as_string())


def setup_logging(name):
    FORMAT = '%(levelname)s %(filename)s:%(lineno)4d: %(message)s'
    # Manually clear root loggers to prevent any module that may have called
    # logging.basicConfig() from blocking our logging setup
    logging.root.handlers = []
    logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout)
    logger = logging.getLogger(name)
    return logger

