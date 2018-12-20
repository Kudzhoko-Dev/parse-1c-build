# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys

from commons.compat import u
from commons.logging_ import add_loggers
from parse_1c_build import logger as main_logger
from parse_1c_build.cli import get_argparser


def run():
    argparser = get_argparser()
    args = argparser.parse_args(u(sys.argv[1:], 'cp1251'))
    add_loggers(args, main_logger)
    args.func(args)
