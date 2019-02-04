# -*- coding: utf-8 -*-
from pathlib import Path
import sys

from parse_1c_build.core import run

sys.path.insert(0, Path(__file__).parent.parent)

if __name__ == '__main__':
    run()
