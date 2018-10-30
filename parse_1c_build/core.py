# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys

from commons.compat import u
from parse_1c_build.cli import get_argparser


def run():
    argparser = get_argparser()
    args = argparser.parse_args(u(sys.argv[1:], 'cp1251'))
    args.func(args)
