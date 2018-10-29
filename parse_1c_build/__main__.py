# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import sys

from parse_1c_build.core import run

sys.path.insert(0, os.path.abspath(os.path.join(__file__, os.pardir, os.pardir)))

if __name__ == '__main__':
    run()
