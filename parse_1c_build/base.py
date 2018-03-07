# -*- coding: utf-8 -*-
from collections import OrderedDict
from pathlib import Path
from typing import Any

from appdirs import site_data_dir, user_data_dir
from commons_1c import get_last_1c_exe_file_path
from parse_1c_build import APP_AUTHOR, APP_NAME
import yaml
import yodl


def get_settings() -> OrderedDict:
    # Settings
    settings_file_path = Path('settings.yaml')
    if not settings_file_path.is_file():
        settings_file_path = Path(user_data_dir(APP_NAME, APP_AUTHOR, roaming=True)) / settings_file_path.name
        if not settings_file_path.is_file():
            settings_file_path = Path(site_data_dir(APP_NAME, APP_AUTHOR)) / settings_file_path.name
            if not settings_file_path.is_file():
                raise SettingsException('Settings file does not exist!')

    with settings_file_path.open(encoding='utf-8') as settings_file:
        settings = yaml.load(settings_file, yodl.OrderedDictYAMLLoader)

    return settings


class Processor:
    def __init__(self) -> None:
        settings = get_settings()

        if 'General' not in settings:
            raise SettingsException('There is no dict \'General\' in settings!')

        settings_general = settings['General']

        self.last_1c_exe_file_path = None
        if '1C' in settings_general:
            self.last_1c_exe_file_path = Path(settings_general['1C'])
        if self.last_1c_exe_file_path is None or not self.last_1c_exe_file_path.is_file():
            self.last_1c_exe_file_path = get_last_1c_exe_file_path()
            if self.last_1c_exe_file_path is None:
                raise Exception('Couldn\'t find 1C:Enterprise 8!')

        if 'IB' not in settings_general:
            raise SettingsException('There is no service information base in settings!')
        self.ib_dir_path = Path(settings_general['IB'])
        if not self.ib_dir_path.is_dir():
            raise Exception('Service information base does not exist!')

        if 'V8Reader' not in settings_general:
            raise SettingsException('There is no V8Reader in settings!')
        self.v8_reader_file_path = Path(settings_general['V8Reader'])
        if not self.v8_reader_file_path.is_file():
            raise Exception('V8Reader does not exist!')

        if 'V8Unpack' not in settings_general:
            raise SettingsException('There is no V8Unpack in settings!')
        self.v8_unpack_file_path = Path(settings_general['V8Unpack'])
        if not self.v8_unpack_file_path.is_file():
            raise Exception('V8Unpack does not exist!')

        if 'GComp' not in settings_general:
            raise SettingsException('There is no GComp in settings!')
        self.gcomp_file_path = Path(settings_general['GComp'])
        if not self.gcomp_file_path.is_file():
            raise Exception('GComp does not exist!')

    def run(self, args: Any) -> None:
        pass


class SettingsException(Exception):
    pass
