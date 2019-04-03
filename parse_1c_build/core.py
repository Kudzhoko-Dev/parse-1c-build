# -*- coding: utf-8 -*-
import sys

from cjk_commons.logging_ import add_loggers
from parse_1c_build import logger as main_logger
from parse_1c_build.cli import get_argparser


def run() -> None:
    argparser = get_argparser()
    args = argparser.parse_args(sys.argv[1:])
    add_loggers(args, main_logger)
    args.func(args)
