# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import os
import shutil
import subprocess
import tempfile

from commons.compat import u
from commons.settings import SettingsError
from commons_1c import platform_
from .base import Processor, add_generic_arguments


class Parser(Processor):
    def get_last_1c_exe_file_fullname(self, **kwargs):
        if '1c' in kwargs:
            last_1c_exe_file_fullname = kwargs['1c']
        else:
            last_1c_exe_file_fullname = self.settings.get('1c', '')
        if not last_1c_exe_file_fullname or not os.path.isfile(last_1c_exe_file_fullname):
            last_1c_exe_file_fullname = platform_.get_last_1c_exe_file_fullname()
            if not last_1c_exe_file_fullname:
                raise IOError(errno.ENOENT, 'Couldn\'t find 1C:Enterprise 8')
        return last_1c_exe_file_fullname

    def get_ib_dir_fullname(self, **kwargs):
        if 'ib_dir' in kwargs:
            ib_dir_fullname = kwargs['ib_dir']
        else:
            if 'ib_dir' not in self.settings:
                raise SettingsError('There is no service information base in settings')
            ib_dir_fullname = self.settings.get('ib_dir', '')
        if not os.path.isdir(ib_dir_fullname):
            raise IOError(errno.ENOENT, 'Service information base does not exist')
        return ib_dir_fullname

    def get_v8_reader_file_fullname(self, **kwargs):
        if 'v8reader_file' in kwargs:
            v8_reader_file_fullname = kwargs['v8reader_file']
        else:
            if 'v8reader_file' not in self.settings:
                raise SettingsError('There is no V8Reader in settings')
            v8_reader_file_fullname = self.settings.get('v8reader_file', '')
        if not os.path.isfile(v8_reader_file_fullname):
            raise IOError(errno.ENOENT, 'V8Reader does not exist')
        return v8_reader_file_fullname

    def run(self, input_file_fullname, output_dir_fullname):
        with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            input_file_fullname_suffix_lower = os.path.splitext(input_file_fullname)[1].lower()
            if input_file_fullname_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
                bat_file.write('"{0}" /F "{1}" /DisableStartupMessages /Execute "{2}" {3}'.format(
                    self.get_last_1c_exe_file_fullname(),
                    self.get_ib_dir_fullname(),
                    self.get_v8_reader_file_fullname(),
                    '/C "decompile;pathToCF;{0};pathOut;{1};shutdown;convert-mxl2txt;"'.format(
                        input_file_fullname,
                        output_dir_fullname
                    )
                ).encode('cp866'))
            elif input_file_fullname_suffix_lower in ['.ert', '.md']:
                input_file_fullname_ = input_file_fullname
                if input_file_fullname_suffix_lower == '.md':
                    temp_dir_fullname = u(tempfile.mkdtemp(), 'cp1251')
                    input_file_fullname_ = os.path.join(temp_dir_fullname, os.path.basename(input_file_fullname_))
                    shutil.copy(input_file_fullname, input_file_fullname_)
                bat_file.write('"{0}" -d -F "{1}" -DD "{2}"'.format(
                    self.get_gcomp_file_fullname(),
                    input_file_fullname_,
                    output_dir_fullname
                ).encode('cp866'))
        exit_code = subprocess.check_call(['cmd.exe', '/C', u(bat_file.name, 'cp1251')])
        if exit_code != 0:
            raise Exception('Parsing \'{0}\' is failed'.format(input_file_fullname))
        os.remove(u(bat_file.name, 'cp1251'))


def run(args):
    processor = Parser()
    # Args
    input_file_fullname = os.path.abspath(u(args.input[0], 'cp1251'))
    if u(args.output, 'cp1251') is None:
        output_dir_fullname = os.path.abspath(
            os.path.splitext(input_file_fullname)[0] + '_' + os.path.splitext(input_file_fullname)[1][1:] + '_src')
    else:
        output_dir_fullname = os.path.abspath(u(args.output, 'cp1251'))
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
    add_generic_arguments(subparser)
