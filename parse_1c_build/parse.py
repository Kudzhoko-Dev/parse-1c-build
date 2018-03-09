# -*- coding: utf-8 -*-
from collections import OrderedDict
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from commons_1c import get_last_1c_exe_file_path
from cujoko_commons import SettingsException, get_settings
from parse_1c_build import APP_AUTHOR, APP_NAME
from parse_1c_build.base import Processor


class Parser(Processor):
    def __init__(self, args: Any, settings: OrderedDict) -> None:
        super().__init__(args, settings)

        self.last_1c_exe_file_path = None
        if '1C' in self.settings_general:
            self.last_1c_exe_file_path = Path(self.settings_general['1C'])
        if self.last_1c_exe_file_path is None or not self.last_1c_exe_file_path.is_file():
            self.last_1c_exe_file_path = get_last_1c_exe_file_path()
            if self.last_1c_exe_file_path is None:
                raise Exception('Couldn\'t find 1C:Enterprise 8!')

        if 'IB' not in self.settings_general:
            raise SettingsException('There is no service information base in settings!')
        self.ib_dir_path = Path(self.settings_general['IB'])
        if not self.ib_dir_path.is_dir():
            raise Exception('Service information base does not exist!')

        if 'V8Reader' not in self.settings_general:
            raise SettingsException('There is no V8Reader in settings!')
        self.v8_reader_file_path = Path(self.settings_general['V8Reader'])
        if not self.v8_reader_file_path.is_file():
            raise Exception('V8Reader does not exist!')

    def parse(self, input_file_path: Path, output_dir_path: Path) -> None:
        with tempfile.NamedTemporaryFile('w', encoding='cp866', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            input_file_path_suffix_lower = input_file_path.suffix.lower()
            if input_file_path_suffix_lower in ['.epf', '.erf']:
                bat_file.write('"{}" /F"{}" /DisableStartupMessages /Execute"{}" {}'.format(
                    str(self.last_1c_exe_file_path),
                    str(self.ib_dir_path),
                    str(self.v8_reader_file_path),
                    '/C"decompile;pathtocf;{};pathout;{};shutdown;convert-mxl2txt;"'.format(
                        str(input_file_path),
                        str(output_dir_path)
                    )
                ))
            elif input_file_path_suffix_lower in ['.ert', '.md']:
                input_file_path_ = input_file_path

                if input_file_path_suffix_lower == '.md':  # fixme Тут что-то непонятное и скорее всего неработоспособное
                    temp_dir_name = tempfile.mkdtemp()
                    input_file_path_ = Path(shutil.copy(str(input_file_path_), temp_dir_name))

                bat_file.write('"{}" -d -F "{}" -DD "{}"'.format(
                    str(self.gcomp_file_path),
                    str(input_file_path_),
                    str(output_dir_path)
                ))

        exit_code = subprocess.check_call(['cmd.exe', '/C', str(bat_file.name)])
        if not exit_code == 0:
            raise Exception('Parsing \'{}\' is failed!'.format(str(input_file_path)))

        Path(bat_file.name).unlink()

    def run(self) -> None:
        input_file_path = Path(self.args.input[0])

        if self.args.output is None:
            output_dir_path = input_file_path.stem + '_' + input_file_path.suffix[1:] + '_src'
        else:
            output_dir_path = Path(self.args.output)

        self.parse(input_file_path, output_dir_path)


def run(args: Any) -> None:
    settings = get_settings(APP_NAME, APP_AUTHOR)
    processor = Parser(args, settings)
    processor.run()


def add_subparser(subparsers: Any) -> None:
    desc = 'Parse 1C:Enterprise file in a directory'
    subparser = subparsers.add_parser(
        Path(__file__).stem,
        help=desc,
        description=desc,
        add_help=False)

    subparser.set_defaults(func=run)

    subparser.add_argument(
        '-h', '--help',
        action='help',
        help='Show this help message and exit')

    subparser.add_argument(
        'input',
        nargs=1)  # todo Добавить help

    subparser.add_argument(
        'output',
        nargs='?')  # todo Добавить help
