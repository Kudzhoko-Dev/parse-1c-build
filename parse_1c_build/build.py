# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import codecs
import errno
import logging
import os
import shutil
import subprocess
import tempfile

from commons.compat import u
from commons.settings import SettingsError
from parse_1c_build.base import Processor, add_generic_arguments

logger = logging.getLogger(__name__)


class Builder(Processor):
    @staticmethod
    def get_temp_source_dir_fullname(input_dir_fullname):
        temp_source_dir_fullname = u(tempfile.mkdtemp(), 'cp1251')
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

    def get_v8_unpack_file_fullname(self, **kwargs):
        if 'v8unpack_file' in kwargs:
            v8_unpack_file_fullname = kwargs['v8unpack_file']
        else:
            if 'v8unpack_file' not in self.settings:
                raise SettingsError('There is no V8Unpack in settings')
            v8_unpack_file_fullname = self.settings.get('v8unpack_file', '')
        if not os.path.isfile(v8_unpack_file_fullname):
            raise IOError(errno.ENOENT, 'V8Unpack does not exist')
        return v8_unpack_file_fullname

    def run(self, input_dir_fullname, output_file_fullname):
        output_file_fullname_suffix_lower = os.path.splitext(output_file_fullname)[1].lower()
        if output_file_fullname_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
            temp_source_dir_fullname = Builder.get_temp_source_dir_fullname(input_dir_fullname)
            exit_code = subprocess.check_call([
                self.get_v8_unpack_file_fullname(),
                '-B',
                temp_source_dir_fullname,
                output_file_fullname
            ])
            if exit_code != 0:
                raise Exception('Building \'{0}\' is failed'.format(output_file_fullname))
            shutil.rmtree(temp_source_dir_fullname)
        elif output_file_fullname_suffix_lower in ['.ert', '.md']:
            # todo Может быть такое, что md-файл будет занят, тогда при его записи возникнет ошибка
            with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
                bat_file.write('@echo off\n')
                bat_file.write('{0} '.format(self.get_gcomp_file_fullname()).encode('cp866'))
                if output_file_fullname_suffix_lower == '.ert':
                    bat_file.write('--external-report ')
                elif output_file_fullname_suffix_lower == '.md':
                    bat_file.write('--meta-data ')
                bat_file.write('-c -F "{0}" -DD "{1}"\n'.format(
                    output_file_fullname,
                    input_dir_fullname
                ).encode('cp866'))
                bat_file.close()
                exit_code = subprocess.check_call(['cmd.exe', '/C', u(bat_file.name, 'cp1251')])
                if exit_code != 0:
                    raise Exception('Building \'{0}\' is failed'.format(output_file_fullname))
            if bat_file:
                os.remove(u(bat_file.name, 'cp1251'))


def run(args):
    try:
        processor = Builder()
        # Args
        input_dir_fullname = os.path.abspath(args.input[0])
        if args.output is None:
            output_file_name = os.path.basename(input_dir_fullname).rpartition('_')[0]
            parts = output_file_name.rpartition('_')
            output_file_fullname = os.path.abspath('{0}.{1}'.format(parts[0], parts[2]))
        else:
            output_file_fullname = os.path.abspath(args.output)
        processor.run(input_dir_fullname, output_file_fullname)
    except Exception as e:
        logger.exception(e)


def add_subparser(subparsers):
    desc = 'Build files in a directory to 1C:Enterprise file'
    subparser = subparsers.add_parser(
        os.path.splitext(os.path.basename(__file__))[0],
        help=desc,
        description=desc,
        add_help=False
    )
    subparser.set_defaults(func=run)
    add_generic_arguments(subparser)
