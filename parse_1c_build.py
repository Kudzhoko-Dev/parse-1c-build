#! python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from appdirs import user_data_dir
from configparser import RawConfigParser
from pathlib import Path
import tempfile
import re
import shutil
import subprocess


__version__ = '2.1.0'

APP_AUTHOR = 'util-1c'
APP_NAME = 'parse-1c-build'

pattern_version = re.compile(r'\D*(?P<version>(\d+)\.(\d+)\.(\d+)\.(\d+))\D*')


class Processor:
    def __init__(self):
        self.argparser = ArgumentParser()
        self.argparser.add_argument('-v', '--version', action='version', version='%(prog)s, ver. {}'.format(
            __version__))
        self.argparser.add_argument('--debug', action='store_true', default=False,
                                    help='if this option exists then debug mode is enabled')

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

        self.exe_1c = None
        if '1C' in self.general_section:
            self.exe_1c = Path(self.general_section['1C'])
        if self.exe_1c is None or not self.exe_1c.is_file():
            self.exe_1c = Processor.get_last_exe_1c()
            if self.exe_1c is None:
                raise SettingsError('1C:Enterprise 8 does not exist!')

        self.ib = Path(self.general_section['IB'])
        if not self.ib.is_dir():
            raise SettingsError('Service information base does not exist!')

        self.v8_reader = Path(self.general_section['V8Reader'])
        if not self.v8_reader.is_file():
            raise SettingsError('V8Reader does not exist!')

        self.v8_unpack = Path(self.general_section['V8Unpack'])
        if not self.v8_unpack.is_file():
            raise SettingsError('V8Unpack does not exist!')

        self.gcomp = Path(self.general_section['GComp'])
        if not self.gcomp.is_file():
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

        estart_path = Path(user_data_dir('1CEStart', '1C', roaming=True)) / '1CEStart.cfg'
        installed_location_paths = []
        if estart_path.is_file():
            with estart_path.open(encoding='utf-16') as estart_file:
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

            platform_versions1 = sorted(platform_versions, key=lambda x: x[0], reverse=True)
            if platform_versions1:
                result = platform_versions1[0][1]
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

    def parse(self, input_path: Path, output_path: Path):
        with tempfile.NamedTemporaryFile('w', encoding='cp866', suffix='.bat', delete=False) as bat_file:
            bat_file.write('@echo off\n')
            in_path_suffix_lower = input_path.suffix.lower()
            if in_path_suffix_lower in ['.epf', '.erf']:
                bat_file.write('"{}" /F"{}" /DisableStartupMessages /Execute"{}" {}'.format(
                    str(self.exe_1c),
                    str(self.ib),
                    str(self.v8_reader),
                    '/C"decompile;pathtocf;{};pathout;{};shutdown;convert-mxl2txt;"'.format(
                        str(input_path),
                        str(output_path)
                    )
                ))
            elif in_path_suffix_lower in ['.ert', '.md']:
                input_path_ = input_path

                if in_path_suffix_lower == '.md':
                    tmp_dir = tempfile.mkdtemp()
                    input_path_ = Path(shutil.copy(str(input_path_), tmp_dir))

                bat_file.write('"{}" -d -F "{}" -DD "{}"'.format(
                    str(self.gcomp),
                    str(input_path_),
                    str(output_path)
                ))

        exit_code = subprocess.check_call(['cmd.exe', '/C', str(bat_file.name)])
        if not exit_code == 0:
            raise Exception('Parsing "{}" is failed!'.format(str(input_path)))

        Path(bat_file.name).unlink()

    def run(self):
        args = self.argparser.parse_args()

        input_path = Path(args.input)
        output_path = Path(args.output)
        self.parse(input_path, output_path)


class Builder(Processor):
    def __init__(self):
        super().__init__()

        self.argparser.add_argument('input', nargs='?')
        self.argparser.add_argument('output', nargs='?')

    def get_temp_source_folder(self, input_path: Path):
        temp_source_folder = Path(tempfile.mkdtemp())
        if not temp_source_folder.is_dir():
            temp_source_folder.mkdir(parents=True)
        else:
            shutil.rmtree(str(temp_source_folder), ignore_errors=True)

        renames_file = input_path / 'renames.txt'

        with renames_file.open(encoding='utf-8-sig') as file:
            for line in file:
                names = line.split('-->')

                new_path = temp_source_folder / names[0].strip()
                new_folder_path = new_path.parent

                if not new_folder_path.is_dir():
                    new_folder_path.mkdir(parents=True)

                old_path = input_path / names[1].strip()

                if old_path.is_dir():
                    new_path = temp_source_folder / names[0].strip()
                    shutil.copytree(str(old_path), str(new_path))
                else:
                    shutil.copy(str(old_path), str(new_path))

        return temp_source_folder

    def build_raw(self, temp_source_folder: Path, output_path: Path):
        exit_code = subprocess.check_call([
            str(self.v8_unpack),
            '-B',
            str(temp_source_folder),
            str(output_path)
        ])

        if not exit_code == 0:
            raise Exception('Building "{}" is failed!'.format(str(output_path)))

    def build(self, input_path: Path, output_path: Path):
        temp_source_folder = self.get_temp_source_folder(input_path)
        self.build_raw(temp_source_folder, output_path)

    def run(self):
        args = self.argparser.parse_args()

        input_path = Path(args.input)
        output_path = Path(args.output)
        self.build(input_path, output_path)


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
