# -*- coding: utf-8 -*-
from collections import OrderedDict
from pathlib import Path
from typing import Any

from cujoko_commons import SettingsException


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
