# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from commons.compat import Path
from commons.settings import SettingsError, get_settings
from parse_1c_build import APP_AUTHOR, APP_NAME


class Processor:
    def __init__(self, **kwargs):
        settings_file_path = Path('settings.yaml')
        if 'settings_file' in kwargs:
            settings_file_path = Path(kwargs['settings_file'])
        self.settings = get_settings(settings_file_path, app_name=APP_NAME, app_author=APP_AUTHOR)
        # GComp
        if 'gcomp' in kwargs:
            self.gcomp_file_path = Path(kwargs['gcomp'])
        else:
            if 'gcomp' not in self.settings:
                raise SettingsError('There is no GComp in settings')
            self.gcomp_file_path = Path(self.settings['gcomp'])
        if not self.gcomp_file_path.is_file():
            raise FileNotFoundError('GComp does not exist')
