# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import subprocess
import tempfile

import shutil

from commons.settings import SettingsError
from parse_1c_build.base import Processor, add_generic_arguments

logger = logging.getLogger(__name__)


class Builder(Processor):
    @staticmethod
    def get_temp_source_dir_fullpath(input_dir_fullpath: Path) -> Path:
        temp_source_dir_fullpath = Path(tempfile.mkdtemp())
        renames_file_fullpath = Path(input_dir_fullpath, 'renames.txt')
        with renames_file_fullpath.open(encoding='utf-8-sig') as renames_file:
            for line in renames_file:
                names = line.split('-->')
                new_fullpath = temp_source_dir_fullpath / names[0].strip()
                new_dir_fullpath = Path(new_fullpath).parent.absolute()
                if not new_dir_fullpath.is_dir():
                    new_dir_fullpath.mkdir(parents=True)
                old_fullpath = Path(input_dir_fullpath, names[1].strip())
                if old_fullpath.is_dir():
                    new_fullpath = Path(temp_source_dir_fullpath, names[0].strip())
                    shutil.copytree(old_fullpath, new_fullpath)
                else:
                    shutil.copy(old_fullpath, new_fullpath)
        return temp_source_dir_fullpath

    def get_v8_unpack_file_fullpath(self, **kwargs) -> Path:
        if 'v8unpack_file_path' in kwargs:
            v8_unpack_file_fullpath = Path(kwargs['v8unpack_file_path'])
        else:
            if 'v8unpack_file_path' not in self.settings:
                raise SettingsError('There is no V8Unpack in settings')
            v8_unpack_file_fullpath = Path(self.settings.get('v8unpack_file_path', ''))
        if not v8_unpack_file_fullpath.is_file():
            raise FileExistsError('V8Unpack does not exist')
        return v8_unpack_file_fullpath

    def run(self, input_dir_fullpath: Path, output_file_fullpath: Path) -> None:
        output_file_fullpath_suffix_lower = output_file_fullpath.suffix.lower()
        if output_file_fullpath_suffix_lower in ['.cf', '.cfu', '.epf', '.erf']:
            temp_source_dir_fullpath = Builder.get_temp_source_dir_fullpath(input_dir_fullpath)
            exit_code = subprocess.check_call([
                self.get_v8_unpack_file_fullpath(),
                '-B',
                str(temp_source_dir_fullpath),
                str(output_file_fullpath)
            ])
            if exit_code != 0:
                raise Exception('Building \'{0}\' is failed'.format(output_file_fullpath))
            shutil.rmtree(temp_source_dir_fullpath)
        elif output_file_fullpath_suffix_lower in ['.ert', '.md']:
            # todo Может быть такое, что md-файл будет занят, тогда при его записи возникнет ошибка
            with tempfile.NamedTemporaryFile('w', suffix='.bat', delete=False) as bat_file:
                bat_file.write('@echo off\n')
                bat_file.write('{0} '.format(self.get_gcomp_file_fullpath()).encode('cp866'))
                if output_file_fullpath_suffix_lower == '.ert':
                    bat_file.write('--external-report ')
                elif output_file_fullpath_suffix_lower == '.md':
                    bat_file.write('--meta-data ')
                bat_file.write('-c -F "{0}" -DD "{1}"\n'.format(
                    output_file_fullpath,
                    input_dir_fullpath
                ).encode('cp866'))
                bat_file.close()
                exit_code = subprocess.check_call(['cmd.exe', '/C', bat_file.name])
                if exit_code != 0:
                    raise Exception('Building \'{0}\' is failed'.format(output_file_fullpath))
            if bat_file:
                Path(bat_file.name).unlink()


def run(args) -> None:
    try:
        processor = Builder()
        # Args
        input_dir_fullpath = Path(args.input[0]).absolute()
        if args.output is None:
            output_file_name_and_extension_str = input_dir_fullpath.name.rpartition('_')[0]
            output_file_name_and_extension = output_file_name_and_extension_str.rpartition('_')
            output_file_fullpath = Path(
                '{0}.{1}'.format(output_file_name_and_extension[0], output_file_name_and_extension[2])).absolute()
        else:
            output_file_fullpath = Path(args.output).absolute()
        processor.run(input_dir_fullpath, output_file_fullpath)
    except Exception as e:
        logger.exception(e)


def add_subparser(subparsers) -> None:
    desc = 'Build files in a directory to 1C:Enterprise file'
    subparser = subparsers.add_parser(
        Path(__file__).stem,
        help=desc,
        description=desc,
        add_help=False
    )
    subparser.set_defaults(func=run)
    add_generic_arguments(subparser)
