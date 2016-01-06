import logging
import os

__author__ = 'aparnaelangovan'


def setup_log(dir, name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

# create a file handler

    handler = logging.FileHandler(os.path.join(dir, "log.log"))
    handler.setLevel(logging.INFO)

# create a logging format

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

# add the handlers to the logger

    logger.addHandler(handler)
    return logger