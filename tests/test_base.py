# -*- coding: utf-8 -*-
from pathlib import Path
import unittest

from parse_1c_build.base import Processor
from parse_1c_build.cli import get_argparser


class MainTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = get_argparser()

    def test_processor_1(self) -> None:
        with self.assertRaisesRegex(Exception, r'There is no GComp in settings'):
            Processor(settings_file_path=Path('tests/data/settings.yaml'))

    def test_processor_2(self) -> None:
        with self.assertRaisesRegex(Exception, r'GComp does not exist'):
            Processor(gcomp_file_path=Path(''))  # todo
