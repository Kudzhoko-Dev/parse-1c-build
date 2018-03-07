# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from parse_1c_build.base import Processor


class Parser(Processor):
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
            raise Exception('Parsing "{}" is failed!'.format(str(input_file_path)))

        Path(bat_file.name).unlink()

    def run(self, args: Any) -> None:
        input_file_path = Path(args.input[0])

        if args.output is None:
            output_dir_path = input_file_path.stem + '_' + input_file_path.suffix[1:] + '_src'
        else:
            output_dir_path = Path(args.output)

        self.parse(input_file_path, output_dir_path)


def run(args: Any) -> None:
    Parser().run(args)


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
