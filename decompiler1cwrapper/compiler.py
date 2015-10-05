#! python3
# -*- coding: utf-8 -*-
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys

from decompiler1cwrapper.generic import Processor

__version__ = '0.1.0'


class Compiler(Processor):
    def __init__(self, settings_file_name: str=''):
        if not settings_file_name:
            settings_file_name = 'decompiler-1c-wrapper.ini'
        super().__init__(settings_file_name)

        self.argparser.add_argument('input', nargs='?')
        self.argparser.add_argument('output', nargs='?')

    def perform(self, input_folder: Path, output_file: Path):
        temp_source_folder = Path(tempfile.mkdtemp())
        if not temp_source_folder.exists():
            temp_source_folder.mkdir(parents=True)
        else:
            shutil.rmtree(str(temp_source_folder), ignore_errors=True)

        renames_file = input_folder / 'renames.txt'

        with renames_file.open(encoding='utf-8-sig') as file:
            for line in file:
                names = line.split('-->')

                new_path = temp_source_folder / names[0].strip()
                new_folder_path = new_path.parent

                if not new_folder_path.exists():
                    new_folder_path.mkdir(parents=True)

                old_path = input_folder / names[1].strip()

                if old_path.is_dir():
                    new_path = temp_source_folder / names[0].strip()
                    shutil.copytree(str(old_path), str(new_path))
                else:
                    shutil.copy(str(old_path), str(new_path))

        exit_code = subprocess.check_call([
            str(self.v8_unpack),
            '-B',
            str(temp_source_folder),
            str(output_file)
        ])
        if not exit_code == 0:
            raise Exception('Не удалось собрать файл {}'.format(str(output_file)))

    def run(self):
        args = self.argparser.parse_args()

        if args.debug:
            import sys
            sys.path.append('C:\\Python34\\pycharm-debug-py3k.egg')

            import pydevd
            pydevd.settrace(port=10050)

        input_folder = Path(args.input)
        output_file = Path(args.output)

        self.perform(input_folder, output_file)


if __name__ == '__main__':
    decompiler = Compiler('decompiler-1c-wrapper.ini')
    sys.exit(decompiler.run())
