# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import sys
from loguru import logger

from cjk_commons.settings import get_path_attribute
from commons_1c import platform_
from parse_1c_build.base import Processor, add_generic_arguments

logger.disable(__name__)


class Parser(Processor):
    def get_1c_exe_file_fullpath(self, **kwargs) -> Path:
        result = get_path_attribute(kwargs, '1c_file_path', default_path=platform_.get_last_1c_exe_file_fullpath(),
            is_dir=False)
        return result

    def get_ib_dir_fullpath(self, **kwargs) -> Path:
        result = get_path_attribute(kwargs, 'ib_dir_path', self.settings, 'ib_dir', Path('IB'), create_dir=False)
        return result

    def get_v8_reader_file_fullpath(self, **kwargs) -> Path:
        result = get_path_attribute(kwargs, 'v8reader_file_path', self.settings, 'v8reader_file',
            Path('V8Reader/V8Reader.epf'), False)
        return result

    def run(self, input_file_fullpath: Path, output_dir_fullpath: Path = None) -> None:
        input_file_fullpath_suffix_lower = input_file_fullpath.suffix.lower()
        if output_dir_fullpath is None:
            output_dir_fullpath = Path(input_file_fullpath.parent, input_file_fullpath.stem + '_' + input_file_fullpath.suffix[1:] + '_src')
        if input_file_fullpath_suffix_lower in ['.epf', '.erf']:
            if self.use_reader:
                with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False, encoding='cp866') as bat_file:
                    bat_file.write('@echo off\n')

                    command = f'/C "decompile;pathToCF;{input_file_fullpath};pathOut;{output_dir_fullpath};shutdown;convert-mxl2txt;"'

                    bat_file.write(
                        f'"{self.get_1c_exe_file_fullpath()}" /F "{self.get_ib_dir_fullpath()}" /DisableStartupMessages /Execute "{self.get_v8_reader_file_fullpath()}" {command}')
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
                    raise Exception(f'parsing \'{input_file_fullpath}\' failed', exit_code)
            logger.info(f'\'{input_file_fullpath}\' parsed to \'{output_dir_fullpath}\'')
        elif input_file_fullpath_suffix_lower in ['.md', '.ert']:
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
                raise Exception(f'parsing \'{input_file_fullpath}\' failed', exit_code)
            logger.info(f'\'{input_file_fullpath}\' parsed to \'{output_dir_fullpath}\'')
        else:
            raise Exception('Undefined input file type')


def run(args) -> None:
    logger.enable('cjk_commons')
    logger.enable('commons_1c')
    logger.enable(__name__)

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
