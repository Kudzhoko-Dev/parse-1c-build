# -*- coding: utf-8 -*-
from pathlib import Path

from commons import SettingsException, get_settings
from parse_1c_build import APP_AUTHOR, APP_NAME


class Processor:
    def __init__(self, **kwargs) -> None:
        self.settings = get_settings(APP_NAME, APP_AUTHOR)

        # GComp
        if 'gcomp' in kwargs:
            self.gcomp_file_path = Path(kwargs['gcomp'])
        else:
            if 'gcomp' not in self.settings:
                raise SettingsException('There is no GComp in settings!')
            self.gcomp_file_path = Path(self.settings['gcomp'])

        if not self.gcomp_file_path.is_file():
            raise Exception('GComp does not exist!')
