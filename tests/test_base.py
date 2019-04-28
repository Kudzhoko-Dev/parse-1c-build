# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from parse_1c_build.base import Processor


def test_processor_1():
    with pytest.raises(Exception) as e:
        Processor(settings_file_path=Path('tests/data/settings.yaml'))
        assert e == 'There is no GComp in settings'


def test_processor_2():
    with pytest.raises(Exception) as e:
        Processor(gcomp_file_path=Path(''))  # todo
        assert e == 'GComp does not exist'
