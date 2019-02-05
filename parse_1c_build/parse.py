# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import subprocess
import tempfile

import shutil

from commons.settings import SettingsError
from commons_1c import platform_
from parse_1c_build.base import Processor, add_generic_arguments

logger = logging.getLogger(__name__)


class Parser(Processor):
    def get_1c_exe_file_path(self, **kwargs) -> Path:
        onec_exe_file_path = kwargs.get(
            '1c_file_path', Path(self.settings.get('1c_file', platform_.get_last_1c_exe_file_fullpath())))
        if not isinstance(onec_exe_file_path, Path):
            raise SettingsError('Argument "1C File Path" Incorrect')
        if not onec_exe_file_path.is_file():
            raise FileExistsError('1C:Enterprise 8 Platform Not Exist')
        return onec_exe_file_path

    def get_ib_dir_fullpath(self, **kwargs) -> Path:
        ib_dir_path = kwargs.get('ib_dir_path', Path(self.settings.get('ib_dir', 'IB')))
        if not isinstance(ib_dir_path, Path):
            raise SettingsError('Argument "IB Dir Path" Incorrect')
        if not ib_dir_path.is_dir():
            raise FileExistsError('Service Information Base Not Exist')
        return ib_dir_path

    def get_v8_reader_file_fullpath(self, **kwargs) -> Path:
        v8_reader_file_path = kwargs.get(
            'v8reader_file_path', Path(self.settings.get('v8reader_file', 'V8Reader/V8Reader.epf')))
        if not isinstance(v8_reader_file_path, Path):
            raise SettingsError('Argument "V8Reader File Path" Incorrect')
        if not v8_reader_file_path.is_file():
            raise FileExistsError('V8Reader Not Exist')
        return v8_reader_file_path

    def run(self, input_file_fullpath: Path, output_dir_fullpath: Path) -> None:
        with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False, encoding='cp866') as bat_file:
            bat_file.write('@echo off\n')
            input_file_fullpath_suffix_lower = input_file_fullpath.suffix.lower()
            if input_file_fullpath_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
                bat_file.write('"{0}" /F "{1}" /DisableStartupMessages /Execute "{2}" {3}'.format(
                    self.get_1c_exe_file_path(),
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
