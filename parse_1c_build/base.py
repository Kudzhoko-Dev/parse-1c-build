# -*- coding: utf-8 -*-
from pathlib import Path

from commons import SettingsException, get_settings
from parse_1c_build import APP_AUTHOR, APP_NAME


class Processor:
    def __init__(self, **kwargs) -> None:
        # GComp
        if 'gcomp' in kwargs:
            self.gcomp_file_path = Path(kwargs['gcomp'])
        else:
            settings = get_settings(APP_NAME, APP_AUTHOR)

            if 'gcomp' not in settings:
                raise SettingsException('There is no GComp in settings!')
            self.gcomp_file_path = Path(settings['gcomp'])

        if not self.gcomp_file_path.is_file():
            raise Exception('GComp does not exist!')
