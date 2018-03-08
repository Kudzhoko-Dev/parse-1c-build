# -*- coding: utf-8 -*-
from collections import OrderedDict
from pathlib import Path
from typing import Any

from appdirs import site_data_dir, user_data_dir
from parse_1c_build import APP_AUTHOR, APP_NAME
import yaml
import yodl


class Processor:
    def __init__(self, args: Any, settings: OrderedDict) -> None:
        self.args = args
        self.settings = settings

        if 'General' not in settings:
            raise SettingsException('There is no dict \'General\' in settings!')

        self.settings_general = settings['General']

        if 'GComp' not in self.settings_general:
            raise SettingsException('There is no GComp in settings!')
        self.gcomp_file_path = Path(self.settings_general['GComp'])
        if not self.gcomp_file_path.is_file():
            raise Exception('GComp does not exist!')

    def run(self) -> None:
        pass


class SettingsException(Exception):
    pass


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
