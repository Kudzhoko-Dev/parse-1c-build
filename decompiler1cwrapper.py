#! python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from configparser import RawConfigParser
import os
from pathlib import Path
import tempfile
import re
import shutil
import subprocess


__version__ = '1.0.2'

pattern_version = re.compile(r'\D*(?P<version>(\d+)\.(\d+)\.(\d+)\.(\d+))\D*')


def get_version_as_number(version: str):
    result = 0
    m = 10000
    match = pattern_version.match(version)
    if match is not None:
        result = \
            int(match.group(2)) * m ** 3 + \
            int(match.group(3)) * m ** 2 + \
            int(match.group(4)) * m + \
            int(match.group(5))

    return result


def get_last_exe_1c():
    result = None

    all_users_profile_path = Path(os.getenv('ALLUSERSPROFILE'))
    estart_path = all_users_profile_path / '1C'/ '1CEStart' / '1CEStart.cfg'
    installed_location_paths = []
    if estart_path.exists() and estart_path.is_file():
        with estart_path.open(encoding='utf-16') as estart_file:
            for line in estart_file.readlines():
                key_and_value = line.split('=')
                if key_and_value[0] == 'InstalledLocation':
                    value = '='.join(key_and_value[1:])
                    installed_location_paths.append(Path(value.rstrip()))

        platform_versions = []
        for installed_location_path in installed_location_paths:
            if installed_location_path.exists() and installed_location_path.is_dir():
                for p1 in installed_location_path.iterdir():
                    version_as_number = get_version_as_number(str(p1.name))
                    if version_as_number != 0:
                        p2 = p1 / 'bin' / '1cv8.exe'
                        if p2.exists() and p2.is_file():
                            platform_versions.append((version_as_number, p2))

        platform_versions1 = sorted(platform_versions, key=lambda x: x[0], reverse=True)
        if platform_versions1:
            result = platform_versions1[0][1]
    else:
        raise SettingsError('1CEStart.cfg file does not exist!')

    return result


class Processor:
    def __init__(self):
        self.argparser = ArgumentParser()
        self.argparser.add_argument('-v', '--version', action='version', version='%(prog)s, ver. {}'.format(
            __version__))
        self.argparser.add_argument('--debug', action='store_true', default=False,
                                    help='if this option exists then debug mode is enabled')

        settings_file_path = Path('decompiler1cwrapper.ini')
        if not settings_file_path.exists() or not settings_file_path.is_file():
            settings_file_path = Path.home() / settings_file_path
            if not settings_file_path.exists() or not settings_file_path.is_file():
                raise SettingsError('Settings file does not exist!')

        self.config = RawConfigParser()
        self.config.optionxform = lambda option: option
        self.config.read(str(settings_file_path), 'utf-8')
        self.general_section_name = 'General'
        self.general_section = self.config[self.general_section_name]

        self.exe_1c = None
        if '1C' in self.general_section:
            self.exe_1c = Path(self.general_section['1C'])
        if self.exe_1c is None or not self.exe_1c.exists() or not self.exe_1c.is_file():
            self.exe_1c = get_last_exe_1c()
            if self.exe_1c is None:
                raise SettingsError('1C:Enterprise 8 does not exist!')

        self.ib = Path(self.general_section['IB'])
        if not self.ib.exists():
            raise SettingsError('Service information base does not exist!')

        self.v8_reader = Path(self.general_section['V8Reader'])
        if not self.v8_reader.exists():
            raise SettingsError('V8Reader does not exist!')

        self.v8_unpack = Path(self.general_section['V8Unpack'])
        if not self.v8_unpack.exists():
            raise SettingsError('V8Unpack does not exist!')

        self.gcomp = Path(self.general_section['GComp'])
        if not self.gcomp.exists():
            raise SettingsError('GComp does not exist!')

    def run(self):
        pass


class Decompiler(Processor):
    def __init__(self):
        super().__init__()

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
            raise Exception('Decompiling "{}" is failed!'.format(str(in_path)))
        Path(bat_file.name).unlink()

    def run(self):
        args = self.argparser.parse_args()

        input_file = Path(args.input)
        output_folder = Path(args.output)

        self.perform(input_file, output_folder)


class Compiler(Processor):
    def __init__(self):
        super().__init__()

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
            raise Exception('Compiling "{}" is failed!'.format(str(output_file)))

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


class Error(Exception):
    def __init__(self, value=None):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class SettingsError(Error):
    def __init__(self, message: str):
        super().__init__('{}'.format(message))


def decompile():
    # sys.path.append('C:\\Python35\\pycharm-debug-py3k.egg')
    #
    # import pydevd
    # pydevd.settrace(port=10050)

    Decompiler().run()


def compile_():
    # sys.path.append('C:\\Python35\\pycharm-debug-py3k.egg')
    #
    # import pydevd
    # pydevd.settrace(port=10050)

    Compiler().run()


if __name__ == '__main__':
    print(get_last_exe_1c())
