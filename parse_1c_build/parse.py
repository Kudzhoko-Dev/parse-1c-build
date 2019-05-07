# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import shutil

from cjk_commons.settings import get_path_attribute
from commons_1c import platform_
from parse_1c_build.base import Processor, add_generic_arguments

logger = logging.getLogger(__name__)


class Parser(Processor):
    def get_1c_exe_file_fullpath(self, **kwargs) -> Path:
        return get_path_attribute(kwargs, '1c_file_path', default_path=platform_.get_last_1c_exe_file_fullpath(),
                                  is_dir=False)

    def get_ib_dir_fullpath(self, **kwargs) -> Path:
        return get_path_attribute(kwargs, 'ib_dir_path', self.settings, 'ib_dir', Path('IB'), create_dir=False)

    def get_v8_reader_file_fullpath(self, **kwargs) -> Path:
        return get_path_attribute(kwargs, 'v8reader_file_path', self.settings, 'v8reader_file',
                                  Path('V8Reader/V8Reader.epf'), False)

    def run(self, input_file_fullpath: Path, output_dir_fullpath: Path = None) -> None:
        input_file_fullpath_suffix_lower = input_file_fullpath.suffix.lower()
        if output_dir_fullpath is None:
            output_dir_fullpath = Path(input_file_fullpath.parent,
                                       input_file_fullpath.stem + '_' + input_file_fullpath.suffix[1:] + '_src')
        if input_file_fullpath_suffix_lower in ['.epf', '.erf']:
            if self.use_reader:
                with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False, encoding='cp866') as bat_file:
                    bat_file.write('@echo off\n')
                    bat_file.write('"{0}" /F "{1}" /DisableStartupMessages /Execute "{2}" {3}'.format(
                        self.get_1c_exe_file_fullpath(),
                        self.get_ib_dir_fullpath(),
                        self.get_v8_reader_file_fullpath(),
                        '/C "decompile;pathToCF;{0};pathOut;{1};shutdown;convert-mxl2txt;"'.format(
                            input_file_fullpath,
                            output_dir_fullpath
                        )
                    ))
                Path(bat_file.name).unlink()
            else:
                args_au = [
                    str(self.get_v8_unpack_file_fullpath()),
                    '-P',
                    str(input_file_fullpath),
                    str(output_dir_fullpath)
                ]
                exit_code = subprocess.check_call(args_au, stdout=open(os.devnull, 'w'))
                if exit_code:
                    raise Exception('parsing \'{0}\' failed'.format(input_file_fullpath), exit_code)
            logger.info('\'{0}\' parsed to \'{1}\''.format(input_file_fullpath, output_dir_fullpath))
        elif input_file_fullpath_suffix_lower in ['.ert', '.md']:
            input_file_fullpath_ = input_file_fullpath  # todo
            if input_file_fullpath_suffix_lower == '.md':
                temp_dir_fullpath = Path(tempfile.mkdtemp())
                input_file_fullpath_ = Path(temp_dir_fullpath, input_file_fullpath_.name)
                shutil.copyfile(str(input_file_fullpath), str(input_file_fullpath_))
            args_au = [
                str(self.get_gcomp_file_fullpath()),
                '-d',
                '-F',
                str(input_file_fullpath_),
                '-DD',
                str(output_dir_fullpath)
            ]
            exit_code = subprocess.check_call(args_au, stdout=open(os.devnull, 'w'))
            if exit_code:
                raise Exception('parsing \'{0}\' failed'.format(input_file_fullpath), exit_code)
            logger.info('\'{0}\' parsed to \'{1}\''.format(input_file_fullpath, output_dir_fullpath))


def run(args) -> None:
    try:
        processor = Parser()
        # Args
        input_file_fullpath = Path(args.input[0]).absolute()
        output_dir_fullpath = None if args.output is None else Path(args.output).absolute()
        processor.run(input_file_fullpath, output_dir_fullpath)
    except Exception as e:
        logger.exception(e)
        sys.exit(1)


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
