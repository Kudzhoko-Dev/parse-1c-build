# -*- coding: utf-8 -*-
import unittest

from parse_1c_build.base import Processor
from parse_1c_build.cli import get_argparser


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_processor_1(self):
        with self.assertRaisesRegex(Exception, r'There is no GComp in settings!'):
            Processor(gcomp='', settings_file='data/settings.yaml')

    def test_processor_2(self):
        with self.assertRaisesRegex(Exception, r'GComp does not exist!'):
            Processor(gcomp='')
