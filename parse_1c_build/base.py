# -*- coding: utf-8 -*-
from pathlib import Path

from commons.settings import SettingsError, get_settings
from parse_1c_build.__about__ import APP_AUTHOR, APP_NAME


class Processor(object):
    def __init__(self, **kwargs):
        settings_file_path = kwargs.get('settings_file_path', Path('settings.yaml'))
        if not isinstance(settings_file_path, Path):
            raise SettingsError('Argument "Settings File Path" Incorrect')
        self.settings = get_settings(settings_file_path, app_name=APP_NAME, app_author=APP_AUTHOR)

    def get_gcomp_file_fullpath(self, **kwargs) -> Path:
        gcomp_file_fullpath = kwargs.get(
            'gcomp_file_path', Path(self.settings.get('gcomp_file', 'GComp/Release/gcomp.exe'))).absolute()
        if not isinstance(gcomp_file_fullpath, Path):
            raise SettingsError('Argument "GComp File Path" Incorrect')
        if not gcomp_file_fullpath.is_file():
            raise FileExistsError('GComp Not Exists')
        return gcomp_file_fullpath


def add_generic_arguments(subparser) -> None:
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
