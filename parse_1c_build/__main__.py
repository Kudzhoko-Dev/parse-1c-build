# -*- coding: utf-8 -*-
from pathlib import Path
import sys

from parse_1c_build.core import run

sys.path.insert(0, str(Path(__file__).absolute().parent.parent))

if __name__ == '__main__':
    run()
