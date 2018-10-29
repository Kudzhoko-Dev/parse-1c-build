# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys

from parse_1c_build.cli import get_argparser


def run():
    argparser = get_argparser()
    args = argparser.parse_args(sys.argv[1:])
    args.func(args)
