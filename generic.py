#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from configparser import RawConfigParser
from pathlib import Path
import tempfile
import subprocess
import sys


__version__ = '0.2.0'


class Processor():
    def __init__(self, settings_file_name: str):
        self.argparser = ArgumentParser()
        self.argparser.add_argument('-v', '--version', action='version', version='%(prog)s, ver. {}'.format(__version__))
        self.argparser.add_argument('--debug', action='store_true', default=False, help='if this option exists then debug mode '
                                                                                   'is enabled')

        settings_file_path = Path(settings_file_name)
        if not settings_file_path.exists():
            settings_file_path = Path(__file__).parent / settings_file_path
            if not settings_file_path.exists():
                raise SettingsError('Файл настроек не существует!')
        self.config = RawConfigParser()
        self.config.optionxform = lambda option: option
        self.config.read(str(settings_file_path), 'utf-8')
        self.general_section_name = 'General'
        self.general_section = self.config[self.general_section_name]

        self.exe_1c = Path(self.general_section['1C'])
        if not self.exe_1c.exists():
            raise SettingsError('Платформа не существует!')

        self.ib = Path(self.general_section['IB'])
        if not self.ib.exists():
            raise SettingsError('Сервисной информационной базы не существует!')

        self.v8_reader = Path(self.general_section['V8Reader'])
        if not self.v8_reader.exists():
            raise SettingsError('V8Reader не существует!')

        self.v8_unpack = Path(self.general_section['V8Unpack'])
        if not self.v8_unpack.exists():
            raise SettingsError('V8Unpack не существует!')

        self.gcomp = Path(self.general_section['GComp'])
        if not self.gcomp.exists():
            raise SettingsError('GComp не существует!')

    def run(self):
        pass


class Error(Exception):
    def __init__(self, value=None):
        super(Error, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class SettingsError(Error):
    def __init__(self, message: str):
        super().__init__('{}'.format(message))
