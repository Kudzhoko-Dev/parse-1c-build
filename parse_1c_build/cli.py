# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from cjk_commons.logging_ import add_logging_arguments
from parse_1c_build import __version__, build, parse


def get_argparser() -> ArgumentParser:
    parser = ArgumentParser(prog='p1cb', description='Parse and build utilities for 1C:Enterprise', add_help=False)
    parser.add_argument(
        '-h', '--help',
        action='help',
        help='Show this help message and exit'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s, ver. {0}'.format(__version__),
        help='Show version'
    )
    add_logging_arguments(parser)
    subparsers = parser.add_subparsers(dest='subparser_name')
    build.add_subparser(subparsers)
    parse.add_subparser(subparsers)
    return parser
