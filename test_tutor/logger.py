# encoding: utf-8

import logging
import sys

log = logging.getLogger("uiauto")


def setup_logger(log_level="debug", log_file=None):
    """setup root logger with ColoredFormatter."""
    level = log_level.upper()

    # hide traceback when log level is INFO/WARNING/ERROR/CRITICAL
    if level !="DEBUG":
        sys.tracebacklimit = 0

    formatter = logging.Formatter( "%(asctime)s - %(levelname)- %(message)s")

    if log_file:
        handler = logging.FileHandler(log_file,'a')
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(level)

#
#
# log_debug = logger.debug
# log_info = logger.info
# log_error = logger.error
