# -*- coding: utf-8 -*-
import logging
from pathlib import Path
import subprocess
import tempfile

import shutil

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

    def run(self, input_dir_fullpath: Path, output_file_fullpath: Path) -> None:
        output_file_fullpath_suffix_lower = output_file_fullpath.suffix.lower()
        if output_file_fullpath_suffix_lower in ['.epf', '.erf']:
            args_au = [
                str(self.get_v8_unpack_file_fullpath()),
                '-B'
            ]
            if self.use_reader:
                temp_source_dir_fullpath = Builder.get_temp_source_dir_fullpath(input_dir_fullpath)
                args_au += [
                    str(temp_source_dir_fullpath)
                ]
            else:
                args_au += [
                    str(input_dir_fullpath)
                ]
            args_au += [
                str(output_file_fullpath)
            ]
            exit_code = subprocess.check_call(args_au)
            if exit_code != 0:
                raise Exception('Building \'{0}\' is failed'.format(output_file_fullpath))
        elif output_file_fullpath_suffix_lower in ['.ert', '.md']:
            # todo Может быть такое, что md-файл будет занят, тогда при его записи возникнет ошибка
            args_au = [
                str(self.get_gcomp_file_fullpath())
            ]
            if output_file_fullpath_suffix_lower == '.ert':
                args_au += [
                    '--external-report'
                ]
            elif output_file_fullpath_suffix_lower == '.md':
                args_au += [
                    '--meta-data'
                ]
            args_au += [
                '-c',
                '-F',
                str(output_file_fullpath),
                '-DD',
                str(input_dir_fullpath)
            ]
            exit_code = subprocess.check_call(args_au)
            if exit_code != 0:
                raise Exception('Building \'{0}\' is failed'.format(output_file_fullpath))


def run(args) -> None:
    try:
        processor = Builder()
        # Args
        input_dir_fullpath = Path(args.input[0]).absolute()
        if args.output is None:
            output_file_name_and_extension_str = input_dir_fullpath.name.rpartition('_')[0]
            output_file_name_and_extension = output_file_name_and_extension_str.rpartition('_')
            output_file_fullpath = Path('{0}.{1}'.format(output_file_name_and_extension[0],
                                                         output_file_name_and_extension[2])).absolute()
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
