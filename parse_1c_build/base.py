# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import os

from commons.settings import SettingsError, get_settings
from parse_1c_build import APP_AUTHOR, APP_NAME


class Processor(object):
    def __init__(self, **kwargs):
        settings_file_name = 'settings.yaml'
        if 'settings_file' in kwargs:
            settings_file_name = kwargs['settings_file']
        self.settings = get_settings(settings_file_name, app_name=APP_NAME, app_author=APP_AUTHOR)
        # GComp
        if 'gcomp_file' in kwargs:
            self.gcomp_file_fullname = kwargs['gcomp_file']
        else:
            if 'gcomp_file' not in self.settings:
                raise SettingsError('There is no GComp in settings')
            self.gcomp_file_fullname = self.settings['gcomp_file']
        if not os.path.isfile(self.gcomp_file_fullname):
            raise IOError(errno.ENOENT, 'GComp does not exist')
