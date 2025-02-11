import logging

isDebug = True


def info(msg):
    if isDebug:
        logging.info(msg)


def debug(msg):
    if isDebug:
        logging.debug(msg)


def error(msg):
    if isDebug:
        logging.error(msg)


def warning(msg):
    if isDebug:
        logging.warning(msg)
