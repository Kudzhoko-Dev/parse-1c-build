# -*- coding: utf-8 -*-
import errno
from pathlib import Path

from commons.settings import SettingsError, get_settings
from parse_1c_build.__about__ import APP_AUTHOR, APP_NAME


class Processor(object):
    def __init__(self, **kwargs):
        settings_file_path = Path('settings.yaml')
        if 'settings_file_path' in kwargs:
            settings_file_path = Path(kwargs['settings_file_path'])
        self.settings = get_settings(settings_file_path, app_name=APP_NAME, app_author=APP_AUTHOR)

    def get_gcomp_file_fullpath(self, **kwargs) -> Path:
        if 'gcomp_file_path' in kwargs:
            gcomp_file_fullpath = Path(kwargs['gcomp_file_path'])
        else:
            if 'gcomp_file_path' not in self.settings:
                raise SettingsError('There is no GComp in settings')
            gcomp_file_fullpath = Path(self.settings.get('gcomp_file_path', ''))
        if not gcomp_file_fullpath.is_file():
            raise IOError(errno.ENOENT, 'GComp does not exist')
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
