# -*- coding: utf-8 -*-
from pathlib import Path
import shutil
import tempfile
import unittest

from parse_1c_build.base import get_settings
from parse_1c_build.build import Builder
from parse_1c_build.cli import get_argparser
from parse_1c_build.parse import Parser


class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = get_argparser()

        self.settings = get_settings()

    def test_parse(self):
        temp_dir_path = Path(tempfile.mkdtemp())

        args = self.parser.parse_args('parse data\\test.epf {0}'.format(temp_dir_path).split())

        processor = Parser(args, self.settings)
        processor.run()

        shutil.rmtree(str(temp_dir_path))

    def test_build(self):
        temp_file_path = Path(tempfile.mkstemp()[1])

        args = self.parser.parse_args('build data\\test_epf_src {0}'.format(temp_file_path).split())

        processor = Builder(args, self.settings)
        processor.run()

        # Не получается удалить временный файл, так как он занят каким-то процессом
