#!/usr/bin/env python
"""
fix_request_6444.py

MOHC.HadGEM3-GC31-HH.*.Prim*

Convert the further_info_url attribute on HadGEM3-GC31-HH from CMIP6 to
PRIMAVERA appropriately.
"""
import argparse
import logging.config
import sys

import django
django.setup()

from pre_proc_app.models import DataRequest, FileFix


__version__ = '0.1.0b1'

DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_LOG_FORMAT = '%(levelname)s: %(message)s'

logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser(description='Add pre-processing rules.')
    parser.add_argument('-l', '--log-level', help='set logging level to one '
                                                  'of debug, info, warn (the '
                                                  'default), or error')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    args = parser.parse_args()

    return args


def main():
    """
    Main entry point
    """
    ### Atmosphere
    data_reqs = DataRequest.objects.filter(
        source_id__name='HadGEM3-GC31-HH',
        table_id__in=['Prim3hr', 'Prim3hrPt', 'Prim6hr', 'Primday',
                      'PrimdayPt', 'PrimmonZ', 'PrimSIday']
    )

    # Remove existing CMIP6 fix
    further_info_url_fix = FileFix.objects.get(name='FurtherInfoUrlPrimToHttps')
    prim_further_info_fix = FileFix.objects.get(name='FurtherInfoUrlToPrim')

    # This next line could be done more quickly by:
    # further_info_url_fix.datarequest_set.add(*data_reqs)
    # but sqlite3 gives an error of:
    # django.db.utils.OperationalError: too many SQL variables
    for data_req in data_reqs:
        data_req.fixes.remove(further_info_url_fix)
        data_req.fixes.remove(prim_further_info_fix)

    logger.debug('FileFix {} removed from {} data requests.'.
                 format(further_info_url_fix.name, data_reqs.count()))
    logger.debug('FileFix {} removed from {} data requests.'.
                 format(prim_further_info_fix.name, data_reqs.count()))

    ### Ocean
    data_reqs = DataRequest.objects.filter(
        source_id__name='HadGEM3-GC31-HH',
        table_id__in=['PrimOday', 'PrimOmon', 'PrimSIday']
    )

    prim_further_info_fix = FileFix.objects.get(
        name='FurtherInfoUrlToPrim'
    )

    for data_req in data_reqs:
        data_req.fixes.add(prim_further_info_fix)

    logger.debug('FileFix {} added to {} data requests.'.
                 format(prim_further_info_fix.name, data_reqs.count()))


if __name__ == "__main__":
    cmd_args = parse_args()

    # determine the log level
    if cmd_args.log_level:
        try:
            log_level = getattr(logging, cmd_args.log_level.upper())
        except AttributeError:
            logger.setLevel(logging.WARNING)
            logger.error('log-level must be one of: debug, info, warn or error')
            sys.exit(1)
    else:
        log_level = DEFAULT_LOG_LEVEL

    # configure the logger
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': DEFAULT_LOG_FORMAT,
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            }
        }
    })

    # run the code
    main()
