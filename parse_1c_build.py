#! python3.6
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from appdirs import user_data_dir
from configparser import RawConfigParser
import os
from pathlib import Path
import tempfile
import re
import shutil
import subprocess


__version__ = '2.2.0'

APP_AUTHOR = 'util-1c'
APP_NAME = 'parse-1c-build'

pattern_version = re.compile(r'\D*(?P<version>(\d+)\.(\d+)\.(\d+)\.(\d+))\D*')


class Processor:
    def __init__(self):
        self.argparser = ArgumentParser()

        self.argparser.add_argument('-v', '--version', action='version', version='%(prog)s, ver. {}'.format(
            __version__))

        settings_file_path = Path('settings.ini')
        if not settings_file_path.is_file():
            settings_file_path = Path(user_data_dir(APP_NAME, APP_AUTHOR, roaming=True)) / settings_file_path
            if not settings_file_path.is_file():
                raise SettingsError('Settings file does not exist!')

        self.config = RawConfigParser()
        self.config.optionxform = lambda option: option
        self.config.read(str(settings_file_path), 'utf-8')
        self.general_section_name = 'General'
        self.general_section = self.config[self.general_section_name]

        self.exe_1c_file_path = None
        if '1C' in self.general_section:
            self.exe_1c_file_path = Path(self.general_section['1C'])
        if self.exe_1c_file_path is None or not self.exe_1c_file_path.is_file():
            self.exe_1c_file_path = Processor.get_last_exe_1c()
            if self.exe_1c_file_path is None:
                raise SettingsError('1C:Enterprise 8 does not exist!')

        self.ib_dir_path = Path(self.general_section['IB'])
        if not self.ib_dir_path.is_dir():
            raise SettingsError('Service information base does not exist!')

        self.v8_reader_file_path = Path(self.general_section['V8Reader'])
        if not self.v8_reader_file_path.is_file():
            raise SettingsError('V8Reader does not exist!')

        self.v8_unpack_file_path = Path(self.general_section['V8Unpack'])
        if not self.v8_unpack_file_path.is_file():
            raise SettingsError('V8Unpack does not exist!')

        self.gcomp_file_path = Path(self.general_section['GComp'])
        if not self.gcomp_file_path.is_file():
            raise SettingsError('GComp does not exist!')

    @staticmethod
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

    @staticmethod
    def get_last_exe_1c():
        result = None

        estart_file_path = Path(os.getenv('ALLUSERSPROFILE')) / '1C'/ '1CEStart' / '1CEStart.cfg'
        installed_location_paths = []
        if estart_file_path.is_file():
            with estart_file_path.open(encoding='utf-16') as estart_file:
                for line in estart_file.readlines():
                    key_and_value = line.split('=')
                    if key_and_value[0] == 'InstalledLocation':
                        value = '='.join(key_and_value[1:])
                        installed_location_paths.append(Path(value.rstrip()))

            platform_versions = []
            for installed_location_path in installed_location_paths:
                if installed_location_path.is_dir():
                    for p1 in installed_location_path.iterdir():
                        version_as_number = Processor.get_version_as_number(str(p1.name))
                        if version_as_number != 0:
                            p2 = p1 / 'bin' / '1cv8.exe'
                            if p2.is_file():
                                platform_versions.append((version_as_number, p2))

            platform_versions_reversed = sorted(platform_versions, key=lambda x: x[0], reverse=True)
            if platform_versions_reversed:
                result = platform_versions_reversed[0][1]
        else:
            raise SettingsError('1CEStart.cfg file does not exist!')

        return result

    def run(self):
        pass


class Parser(Processor):
    def __init__(self):
        super().__init__()

        self.argparser.add_argument('input', nargs='?')
        self.argparser.add_argument('output', nargs='?')

    def parse(self, input_file_path: Path, output_dir_path: Path):
        with tempfile.NamedTemporaryFile('w', encoding='cp866', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            input_file_path_suffix_lower = input_file_path.suffix.lower()
            if input_file_path_suffix_lower in ['.epf', '.erf']:
                bat_file.write('"{}" /F"{}" /DisableStartupMessages /Execute"{}" {}'.format(
                    str(self.exe_1c_file_path),
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

    def run(self):
        args = self.argparser.parse_args()

        input_file_path = Path(args.input)
        output_dir_path = Path(args.output)
        self.parse(input_file_path, output_dir_path)


class Builder(Processor):
    def __init__(self):
        super().__init__()

        self.argparser.add_argument('input', nargs='?')
        self.argparser.add_argument('output', nargs='?')

    def get_temp_source_dir_path(self, input_dir_path: Path):
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

    def build_raw(self, temp_source_dir_path: Path, output_file_path: Path):
        exit_code = subprocess.check_call([
            str(self.v8_unpack_file_path),
            '-B',
            str(temp_source_dir_path),
            str(output_file_path)
        ])

        if not exit_code == 0:
            raise Exception('Building "{}" is failed!'.format(str(output_file_path)))

    def build(self, input_dir_path: Path, output_file_path: Path):
        temp_source_dir_path = self.get_temp_source_dir_path(input_dir_path)

        self.build_raw(temp_source_dir_path, output_file_path)

        shutil.rmtree(str(temp_source_dir_path))

    def run(self):
        args = self.argparser.parse_args()

        input_dir_path = Path(args.input)
        output_file_path = Path(args.output)
        self.build(input_dir_path, output_file_path)


class Error(Exception):
    def __init__(self, value=None):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class SettingsError(Error):
    def __init__(self, message: str):
        super().__init__('{}'.format(message))


def parse():
    Parser().run()


def build():
    Builder().run()
