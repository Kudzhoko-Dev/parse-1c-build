# -*- coding: utf-8 -*-
from collections import OrderedDict
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Any

from parse_1c_build.base import Processor, SettingsException, get_settings


class Builder(Processor):
    @staticmethod
    def get_temp_source_dir_path(input_dir_path: Path) -> Path:
        temp_source_dir_path = Path(tempfile.mkdtemp())

        renames_file_path = input_dir_path / 'renames.txt'

        with renames_file_path.open(encoding='utf-8-sig') as file:
            for line in file:
                names = line.split('-->')

                new_path = temp_source_dir_path / names[0].strip()
                new_dir_path = new_path.parent

                if not new_dir_path.is_dir():
                    new_dir_path.mkdir(parents=True)

                old_path = input_dir_path / names[1].strip()

                if old_path.is_dir():
                    new_path = temp_source_dir_path / names[0].strip()
                    shutil.copytree(str(old_path), str(new_path))
                else:
                    shutil.copy(str(old_path), str(new_path))

        return temp_source_dir_path

    def __init__(self, args: Any, settings: OrderedDict) -> None:
        super().__init__(args, settings)

        if 'V8Unpack' not in self.settings_general:
            raise SettingsException('There is no V8Unpack in settings!')
        self.v8_unpack_file_path = Path(self.settings_general['V8Unpack'])
        if not self.v8_unpack_file_path.is_file():
            raise Exception('V8Unpack does not exist!')

    def build_raw(self, temp_source_dir_path: Path, output_file_path: Path) -> None:
        exit_code = subprocess.check_call([
            str(self.v8_unpack_file_path),
            '-B',
            str(temp_source_dir_path),
            str(output_file_path)
        ])

        if not exit_code == 0:
            raise Exception('Building \'{}\' is failed!'.format(str(output_file_path)))

    def build(self, input_dir_path: Path, output_file_path: Path, **kwargs) -> None:
        temp_source_dir_path = Builder.get_temp_source_dir_path(input_dir_path)

        self.build_raw(temp_source_dir_path, output_file_path)

        shutil.rmtree(str(temp_source_dir_path))

    def run(self) -> None:
        input_dir_path = Path(self.args.input[0])

        if self.args.output is None:
            output_file_name = input_dir_path.name.rpartition('_')[0]
            parts = output_file_name.rpartition('_')

            output_file_path = Path('{}.{}'.format(parts[0], parts[2]))
        else:
            output_file_path = Path(self.args.output)

        self.build(input_dir_path, output_file_path)


def run(args: Any) -> None:
    settings = get_settings()
    processor = Builder(args, settings)
    processor.run()


def add_subparser(subparsers: Any) -> None:
    desc = 'Build files in a directory to 1C:Enterprise 7.7 file'
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
