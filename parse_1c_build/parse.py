# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import os
import shutil
import subprocess
import tempfile

from commons.compat import s, u
from commons.settings import SettingsError
from commons_1c.platform_ import get_last_1c_exe_file_fullname
from parse_1c_build.base import Processor


class Parser(Processor):
    def __init__(self, **kwargs):
        super(Parser, self).__init__(**kwargs)
        # 1C
        if '1c' in kwargs:
            self.last_1c_exe_file_fullname = kwargs['1c']
        else:
            self.last_1c_exe_file_fullname = None
            if '1c' in self.settings:
                self.last_1c_exe_file_fullname = self.settings['1c']
        if self.last_1c_exe_file_fullname is None or not os.path.isfile(self.last_1c_exe_file_fullname):
            self.last_1c_exe_file_fullname = get_last_1c_exe_file_fullname()
            if self.last_1c_exe_file_fullname is None:
                raise IOError(errno.ENOENT, 'Couldn\'t find 1C:Enterprise 8')
        # IB
        if 'ib' in kwargs:
            self.ib_dir_fullname = kwargs['ib']
        else:
            if 'ib' not in self.settings:
                raise SettingsError('There is no service information base in settings')
            self.ib_dir_fullname = self.settings['ib']
        if not os.path.isdir(self.ib_dir_fullname):
            raise IOError(errno.ENOENT, 'Service information base does not exist')
        # V8Reader
        if 'v8reader' in kwargs:
            self.v8_reader_file_fullname = kwargs['v8reader']
        else:
            if 'v8reader' not in self.settings:
                raise SettingsError('There is no V8Reader in settings')
            self.v8_reader_file_fullname = self.settings['v8reader']
        if not os.path.isfile(self.v8_reader_file_fullname):
            raise IOError(errno.ENOENT, 'V8Reader does not exist')

    def run(self, input_file_fullname, output_dir_fullname):
        temp_dir_fullname = ''
        args_au = []
        input_file_fullname_suffix_lower = os.path.splitext(input_file_fullname)[1].lower()
        if input_file_fullname_suffix_lower in ['.epf', '.erf']:
            args_au += [
                '"{0}" /F"{1}" /DisableStartupMessages /Execute"{2}" {3}'.format(
                    self.last_1c_exe_file_fullname,
                    self.ib_dir_fullname,
                    self.v8_reader_file_fullname,
                    '/C"decompile;pathtocf;{0};pathout;{1};shutdown;convert-mxl2txt;"'.format(
                        input_file_fullname,
                        output_dir_fullname
                    )
                )
            ]
        elif input_file_fullname_suffix_lower in ['.ert', '.md']:
            input_file_fullname_ = input_file_fullname
            temp_dir_fullname = u(tempfile.mkdtemp())
            input_file_fullname_ = os.path.join(temp_dir_fullname, os.path.basename(input_file_fullname_))
            shutil.copy(input_file_fullname, input_file_fullname_)
            args_au += [
                '"{0}" -d -F "{1}" -DD "{2}"'.format(
                    self.gcomp_file_fullname,
                    input_file_fullname_,
                    output_dir_fullname
                )
            ]
        exit_code = subprocess.check_call(s(args_au, encoding='cp1251'))
        if temp_dir_fullname:
            shutil.rmtree(temp_dir_fullname)
        if not exit_code == 0:
            raise Exception('Parsing \'{0}\' is failed'.format(input_file_fullname))


def run(args):
    processor = Parser()
    # Args
    input_file_fullname = args.input[0]
    if args.output is None:
        output_dir_fullname = (
                os.path.splitext(input_file_fullname)[0] + '_' + os.path.splitext(input_file_fullname)[1][1:] + '_src')
    else:
        output_dir_fullname = args.output
    processor.run(input_file_fullname, output_dir_fullname)


def add_subparser(subparsers):
    desc = 'Parse 1C:Enterprise file in a directory'
    subparser = subparsers.add_parser(
        os.path.splitext(os.path.basename(__file__))[0],
        help=desc,
        description=desc,
        add_help=False
    )
    subparser.set_defaults(func=run)
    subparser.add_argument(
        '-h', '--help',
        action='help',
        help='Show this help message and exit'
    )
    # todo Добавить help
    subparser.add_argument(
        'input',
        nargs=1
    )
    # todo Добавить help
    subparser.add_argument(
        'output',
        nargs='?'
    )
