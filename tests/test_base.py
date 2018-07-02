# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import unittest

from six import assertRaisesRegex

from parse_1c_build.base import Processor
from parse_1c_build.cli import get_argparser


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_processor_1(self):
        with assertRaisesRegex(self, Exception, r'There is no GComp in settings'):
            Processor(settings_file='tests/data/settings.yaml')

    def test_processor_2(self):
        with assertRaisesRegex(self, Exception, r'GComp does not exist'):
            Processor(gcomp_file='')
