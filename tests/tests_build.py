# -*- coding: utf-8 -*-
from pathlib import Path
import tempfile
import unittest

from parse_1c_build.build import run as build_run
from parse_1c_build.cli import get_argparser


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_build(self):
        temp_file_path = Path(tempfile.mkstemp()[1])
        args = self.parser.parse_args('build tests/data/test_epf_src {0}'.format(temp_file_path).split())
        build_run(args)
        # Не получается удалить временный файл, так как он занят каким-то процессом
