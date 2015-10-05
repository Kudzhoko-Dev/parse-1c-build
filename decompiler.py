#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from pathlib import Path
import tempfile
import subprocess
import sys

from generic import Processor


__version__ = '0.1.0'


class Decompiler(Processor):
    def __init__(self, settings_file_name: str=''):
        if not settings_file_name:
            settings_file_name = 'settings.ini'
        super().__init__(settings_file_name)

        self.argparser.add_argument('input', nargs='?')
        self.argparser.add_argument('output', nargs='?')

    def perform(self, in_path: Path, out_path: Path):
        with tempfile.NamedTemporaryFile('w', encoding='cp866', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            in_path_suffix_lower = in_path.suffix.lower()
            if in_path_suffix_lower in ['.epf', '.erf']:
                bat_file.write('"{}" /F"{}" /DisableStartupMessages /Execute"{}" {}'.format(
                    str(self.exe_1c),
                    str(self.ib),
                    str(self.v8_reader),
                    '/C"decompile;pathtocf;{};pathout;{};shutdown;convert-mxl2txt;"'.format(
                        str(in_path),
                        str(out_path)
                    )
                ))
            elif in_path_suffix_lower in ['.ert', '.md']:
                bat_file.write('"{}" -d -F "{}" -DD "{}"'.format(
                    str(self.gcomp),
                    str(in_path),
                    str(out_path)
                ))
        exit_code = subprocess.check_call(['cmd.exe', '/C', str(bat_file.name)])
        if not exit_code == 0:
            raise Exception('Не удалось разобрать файл {}'.format(str(in_path)))
        Path(bat_file.name).unlink()

    def run(self):
        args = self.argparser.parse_args()

        if args.debug:
            import sys
            sys.path.append('C:\\Python34\\pycharm-debug-py3k.egg')

            import pydevd
            pydevd.settrace(port=10050)

        input_file = Path(args.input)
        output_folder = Path(args.output)

        self.perform(input_file, output_folder)


if __name__ == '__main__':
    decompiler = Decompiler('settings.ini')
    sys.exit(decompiler.run())
