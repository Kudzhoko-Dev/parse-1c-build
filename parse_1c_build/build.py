# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import codecs
import errno
import os
import shutil
import subprocess
import tempfile

from commons.settings import SettingsError
from parse_1c_build.base import Processor


class Builder(Processor):
    @staticmethod
    def get_temp_source_dir_fullname(input_dir_fullname):
        temp_source_dir_fullname = tempfile.mkdtemp()
        renames_file_fullname = os.path.join(input_dir_fullname, 'renames.txt')
        with codecs.open(renames_file_fullname, encoding='utf-8-sig') as file_:
            for line in file_:
                names = line.split('-->')
                new_fullname = temp_source_dir_fullname / names[0].strip()
                new_dir_fullname = os.path.abspath(os.path.join(new_fullname, os.pardir))
                if not os.path.isdir(new_dir_fullname):
                    # fixme Нужно parents=True
                    os.mkdir(new_dir_fullname)
                old_fullname = os.path.join(input_dir_fullname, names[1].strip())
                if os.path.isdir(old_fullname):
                    new_fullname = os.path.join(temp_source_dir_fullname, names[0].strip())
                    shutil.copytree(old_fullname, new_fullname)
                else:
                    shutil.copy(old_fullname, new_fullname)
        return temp_source_dir_fullname

    def __init__(self, **kwargs):
        super(Builder, self).__init__(**kwargs)
        if 'v8unpack' in kwargs:
            self.v8_unpack_file_fullname = kwargs['v8unpack']
        else:
            if 'v8unpack' not in self.settings:
                raise SettingsError('There is no V8Unpack in settings')
            self.v8_unpack_file_fullname = self.settings['v8unpack']
        if not os.path.isfile(self.v8_unpack_file_fullname):
            raise IOError(errno.ENOENT, 'V8Unpack does not exist')

    def build_raw(self, temp_source_dir_fullname, output_file_fullname):
        exit_code = subprocess.check_call([
            self.v8_unpack_file_fullname,
            '-B',
            temp_source_dir_fullname,
            output_file_fullname
        ])
        if not exit_code == 0:
            raise Exception('Building \'{0}\' is failed'.format(output_file_fullname))

    def run(self, input_dir_fullname, output_file_fullname):
        temp_source_dir_fullname = Builder.get_temp_source_dir_fullname(input_dir_fullname)
        self.build_raw(temp_source_dir_fullname, output_file_fullname)
        shutil.rmtree(temp_source_dir_fullname)


def run(args):
    processor = Builder()
    # Args
    input_dir_fullname = args.input[0]
    if args.output is None:
        output_file_name = os.path.basename(input_dir_fullname).rpartition('_')[0]
        parts = output_file_name.rpartition('_')
        output_file_fullname = '{0}.{1}'.format(parts[0], parts[2])
    else:
        output_file_fullname = args.output
    processor.run(input_dir_fullname, output_file_fullname)


def add_subparser(subparsers):
    desc = 'Build files in a directory to 1C:Enterprise 7.7 file'
    subparser = subparsers.add_parser(
        os.path.splitext(__file__)[0],
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
