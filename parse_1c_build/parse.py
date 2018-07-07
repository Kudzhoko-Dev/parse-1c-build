# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import os
import shutil
import subprocess
import tempfile

from commons.compat import u
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
        if 'ib_dir' in kwargs:
            self.ib_dir_fullname = kwargs['ib_dir']
        else:
            if 'ib_dir' not in self.settings:
                raise SettingsError('There is no service information base in settings')
            self.ib_dir_fullname = self.settings['ib_dir']
        if not os.path.isdir(self.ib_dir_fullname):
            raise IOError(errno.ENOENT, 'Service information base does not exist')
        # V8Reader
        if 'v8reader_file' in kwargs:
            self.v8_reader_file_fullname = kwargs['v8reader_file']
        else:
            if 'v8reader_file' not in self.settings:
                raise SettingsError('There is no V8Reader in settings')
            self.v8_reader_file_fullname = self.settings['v8reader_file']
        if not os.path.isfile(self.v8_reader_file_fullname):
            raise IOError(errno.ENOENT, 'V8Reader does not exist')

    def run(self, input_file_fullname, output_dir_fullname):
        with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            input_file_fullname_suffix_lower = os.path.splitext(input_file_fullname)[1].lower()
            if input_file_fullname_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
                bat_file.write('"{0}" /F "{1}" /DisableStartupMessages /Execute "{2}" {3}'.format(
                    self.last_1c_exe_file_fullname,
                    self.ib_dir_fullname,
                    self.v8_reader_file_fullname,
                    '/C "decompile;pathToCF;{0};pathOut;{1};convert-mxl2txt;"'.format(
                        input_file_fullname,
                        output_dir_fullname
                    )
                ).encode('cp866'))
            elif input_file_fullname_suffix_lower in ['.ert', '.md']:
                input_file_fullname_ = input_file_fullname
                if input_file_fullname_suffix_lower == '.md':
                    temp_dir_fullname = u(tempfile.mkdtemp(), encoding='cp1251')
                    input_file_fullname_ = os.path.join(temp_dir_fullname, os.path.basename(input_file_fullname_))
                    shutil.copy(input_file_fullname, input_file_fullname_)
                bat_file.write('"{0}" -d -F "{1}" -DD "{2}"'.format(
                    self.gcomp_file_fullname,
                    input_file_fullname_,
                    output_dir_fullname
                ).encode('cp866'))
        exit_code = subprocess.check_call(['cmd.exe', '/C', u(bat_file.name, encoding='cp1251')])
        if not exit_code == 0:
            raise Exception('Parsing \'{0}\' is failed'.format(input_file_fullname))
        os.remove(u(bat_file.name, encoding='cp1251'))


def run(args):
    processor = Parser()
    # Args
    input_file_fullname = os.path.abspath(u(args.input[0], encoding='cp1251'))
    if u(args.output, encoding='cp1251') is None:
        output_dir_fullname = os.path.abspath(
                os.path.splitext(input_file_fullname)[0] + '_' + os.path.splitext(input_file_fullname)[1][1:] + '_src')
    else:
        output_dir_fullname = os.path.abspath(u(args.output, encoding='cp1251'))
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
