# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import shutil
import subprocess
import tempfile

from commons.compat import Path
from commons.settings import SettingsError
from parse_1c_build.base import Processor


class Builder(Processor):
    @staticmethod
    def get_temp_source_dir_path(input_dir_path):
        temp_source_dir_path = Path(tempfile.mkdtemp())
        renames_file_path = input_dir_path / 'renames.txt'
        with renames_file_path.open(encoding='utf-8-sig') as file_:
            for line in file_:
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

    def __init__(self, **kwargs):
        super(Builder, self).__init__(**kwargs)
        if 'v8unpack' in kwargs:
            self.v8_unpack_file_path = Path(kwargs['v8unpack'])
        else:
            if 'v8unpack' not in self.settings:
                raise SettingsError('There is no V8Unpack in settings')
            self.v8_unpack_file_path = Path(self.settings['v8unpack'])
        if not self.v8_unpack_file_path.is_file():
            raise IOError(errno.ENOENT, 'V8Unpack does not exist')

    def build_raw(self, temp_source_dir_path, output_file_path):
        exit_code = subprocess.check_call([
            str(self.v8_unpack_file_path),
            '-B',
            str(temp_source_dir_path),
            str(output_file_path)
        ])
        if not exit_code == 0:
            raise Exception('Building \'{0}\' is failed'.format(output_file_path))

    def run(self, input_dir_path, output_file_path):
        temp_source_dir_path = Builder.get_temp_source_dir_path(input_dir_path)
        self.build_raw(temp_source_dir_path, output_file_path)
        shutil.rmtree(str(temp_source_dir_path))


def run(args):
    processor = Builder()
    # Args
    input_dir_path = Path(args.input[0])
    if args.output is None:
        output_file_name = input_dir_path.name.rpartition('_')[0]
        parts = output_file_name.rpartition('_')
        output_file_path = Path('{0}.{1}'.format(parts[0], parts[2]))
    else:
        output_file_path = Path(args.output)
    processor.run(input_dir_path, output_file_path)


def add_subparser(subparsers):
    desc = 'Build files in a directory to 1C:Enterprise 7.7 file'
    subparser = subparsers.add_parser(
        Path(__file__).stem,
        help=desc,
        description=desc,
        add_help=False
    )
    subparser.set_defaults(func=run)
    subparser.add_argument(
        '-h', '--help',
        action='help',
        help='Show this help message and exit'
    )
    # todo Добавить help
    subparser.add_argument(
        'input',
        nargs=1
    )
    # todo Добавить help
    subparser.add_argument(
        'output',
        nargs='?'
    )
