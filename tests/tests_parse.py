# -*- coding: utf-8 -*-
from pathlib import Path
import tempfile
import unittest

import shutil

from parse_1c_build.cli import get_argparser
from parse_1c_build.parse import run as parse_run


class MainTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = get_argparser()

    def test_parse(self) -> None:
        temp_dir_fullpath = Path(tempfile.mkdtemp())
        args = self.parser.parse_args('parse tests/data/test.epf {0}'.format(temp_dir_fullpath).split())
        parse_run(args)
        shutil.rmtree(temp_dir_fullpath)
