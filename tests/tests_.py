# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import tempfile
import unittest

from parse_1c_build.build import run as build_run
from parse_1c_build.cli import get_argparser
from parse_1c_build.parse import run as parse_run


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

    def test_parse(self):
        temp_dir_path = Path(tempfile.mkdtemp())

        args = self.parser.parse_args('parse data\\test.epf {0}'.format(temp_dir_path).split())

        parse_run(args)

        shutil.rmtree(str(temp_dir_path))

    def test_build(self):
        temp_file_path = Path(tempfile.mkstemp()[1])

        args = self.parser.parse_args('build data\\test_epf_src {0}'.format(temp_file_path).split())

        build_run(args)

        # Не получается удалить временный файл, так как он занят каким-то процессом
