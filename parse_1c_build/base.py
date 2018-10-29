# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import os

from commons.settings import SettingsError, get_settings
from . import APP_AUTHOR, APP_NAME


class Processor(object):
    def __init__(self, **kwargs):
        settings_file_name = 'settings.yaml'
        if 'settings_file' in kwargs:
            settings_file_name = kwargs['settings_file']
        self.settings = get_settings(settings_file_name, app_name=APP_NAME, app_author=APP_AUTHOR)

    def get_gcomp_file_fullname(self, **kwargs):
        if 'gcomp_file' in kwargs:
            gcomp_file_fullname = kwargs['gcomp_file']
        else:
            if 'gcomp_file' not in self.settings:
                raise SettingsError('There is no GComp in settings')
            gcomp_file_fullname = self.settings.get('gcomp_file', '')
        if not os.path.isfile(gcomp_file_fullname):
            raise IOError(errno.ENOENT, 'GComp does not exist')
        return gcomp_file_fullname


def add_generic_arguments(subparser):
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
