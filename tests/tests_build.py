# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import tempfile
import unittest

from commons.compat import u
from parse_1c_build.build import run as build_run
from parse_1c_build.cli import get_argparser


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_build(self):
        temp_file_fullname = u(tempfile.mkstemp()[1], 'cp1251')
        args = self.parser.parse_args('build tests/data/test_epf_src {0}'.format(temp_file_fullname).split())
        build_run(args)
        # Не получается удалить временный файл, так как он занят каким-то процессом
