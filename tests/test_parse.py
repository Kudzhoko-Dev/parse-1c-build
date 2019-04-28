# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from parse_1c_build.cli import get_argparser
from parse_1c_build.parse import run as parse_run


@pytest.fixture()
def test(request):
    return get_argparser()


def test_parse(test, tmpdir):
    parser = test

    temp_dir_fullpath = Path(tmpdir)
    args = parser.parse_args('parse tests/data/test.epf {0}'.format(temp_dir_fullpath).split())

    parse_run(args)

    assert Path(temp_dir_fullpath, 'root').exists()
