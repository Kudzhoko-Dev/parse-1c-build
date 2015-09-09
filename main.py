#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
import sys


__version__ = '0.1.0'


def compile_():
    pass


def decompile(exe1c: Path, ib: Path, v8_reader: Path, gcomp: Path):  # fixme
    pass


def main():
    argparser = ArgumentParser()
    argparser.add_argument('-v', '--version', action='version', version='%(prog)s, ver. {}'.format(__version__))
    argparser.add_argument('--debug', action='store_true', default=False, help='if this option exists then debug mode '
                                                                               'is enabled')
    args = argparser.parse_args()

    if args.debug:
        import sys
        sys.path.append('C:\\Python34\\pycharm-debug-py3k.egg')

        import pydevd
        pydevd.settrace(port=10050)


if __name__ == '__main__':
    sys.exit(main())