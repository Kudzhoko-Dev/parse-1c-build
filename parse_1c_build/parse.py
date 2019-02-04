# -*- coding: utf-8 -*-
import errno
import logging
from pathlib import Path
import subprocess
import tempfile

import shutil

from commons.settings import SettingsError
from commons_1c import platform_
from parse_1c_build.base import Processor, add_generic_arguments

logger: logging.Logger = logging.getLogger(__name__)


class Parser(Processor):
    def get_last_1c_exe_file_fullpath(self, **kwargs) -> Path:
        if '1c_file_path' in kwargs:
            last_1c_exe_file_fullpath = Path(kwargs['1c_file_path'])
        else:
            last_1c_exe_file_fullpath = Path(self.settings.get('1c_file_path', ''))
        if not last_1c_exe_file_fullpath or not last_1c_exe_file_fullpath.is_file():
            last_1c_exe_file_fullpath = platform_.get_last_1c_exe_file_fullpath()
            if not last_1c_exe_file_fullpath:
                raise IOError(errno.ENOENT, 'Couldn\'t find 1C:Enterprise 8')
        return last_1c_exe_file_fullpath

    def get_ib_dir_fullpath(self, **kwargs) -> Path:
        if 'ib_dir_path' in kwargs:
            ib_dir_fullpath = Path(kwargs['ib_dir_path'])
        else:
            if 'ib_dir_path' not in self.settings:
                raise SettingsError('There is no service information base in settings')
            ib_dir_fullpath = Path(self.settings.get('ib_dir_path', ''))
        if not ib_dir_fullpath.is_dir():
            raise IOError(errno.ENOENT, 'Service information base does not exist')
        return ib_dir_fullpath

    def get_v8_reader_file_fullpath(self, **kwargs) -> Path:
        if 'v8reader_file_path' in kwargs:
            v8_reader_file_fullpath = Path(kwargs['v8reader_file_path'])
        else:
            if 'v8reader_file_path' not in self.settings:
                raise SettingsError('There is no V8Reader in settings')
            v8_reader_file_fullpath = Path(self.settings.get('v8reader_file', ''))
        if not v8_reader_file_fullpath.is_file():
            raise IOError(errno.ENOENT, 'V8Reader does not exist')
        return v8_reader_file_fullpath

    def run(self, input_file_fullpath: Path, output_dir_fullpath: Path) -> None:
        with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False, encoding='cp866') as bat_file:
            bat_file.write('@echo off\n')
            input_file_fullpath_suffix_lower = input_file_fullpath.suffix.lower()
            if input_file_fullpath_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
                bat_file.write('"{0}" /F "{1}" /DisableStartupMessages /Execute "{2}" {3}'.format(
                    self.get_last_1c_exe_file_fullpath(),
                    self.get_ib_dir_fullpath(),
                    self.get_v8_reader_file_fullpath(),
                    '/C "decompile;pathToCF;{0};pathOut;{1};shutdown;convert-mxl2txt;"'.format(
                        input_file_fullpath,
                        output_dir_fullpath
                    )
                ))
            elif input_file_fullpath_suffix_lower in ['.ert', '.md']:
                input_file_fullpath_ = input_file_fullpath  # todo
                if input_file_fullpath_suffix_lower == '.md':
                    temp_dir_fullpath = Path(tempfile.mkdtemp())
                    input_file_fullpath_ = Path(temp_dir_fullpath, input_file_fullpath_.name)
                    shutil.copyfile(str(input_file_fullpath), str(input_file_fullpath_))
                bat_file.write('"{0}" -d -F "{1}" -DD "{2}"'.format(
                    self.get_gcomp_file_fullpath(),
                    input_file_fullpath_,
                    output_dir_fullpath
                ))
        exit_code = subprocess.check_call(['cmd.exe', '/C', bat_file.name])
        if exit_code != 0:
            raise Exception('Parsing \'{0}\' is failed'.format(input_file_fullpath))
        Path(bat_file.name).unlink()


def run(args) -> None:
    try:
        processor = Parser()
        # Args
        input_file_fullpath = Path(args.input[0]).absolute()
        if args.output is None:
            output_dir_fullpath = Path(
                input_file_fullpath.parent, input_file_fullpath.stem + '_' + input_file_fullpath.suffix[1:] + '_src')
        else:
            output_dir_fullpath = Path(args.output).absolute()
        processor.run(input_file_fullpath, output_dir_fullpath)
    except Exception as e:
        logger.exception(e)


def add_subparser(subparsers) -> None:
    desc = 'Parse 1C:Enterprise file in a directory'
    subparser = subparsers.add_parser(
        Path(__file__).stem,
        help=desc,
        description=desc,
        add_help=False
    )
    subparser.set_defaults(func=run)
    add_generic_arguments(subparser)
