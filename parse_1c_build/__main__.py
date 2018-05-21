# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import sys

from parse_1c_build.core import run

file_fullname = os.path.abspath(__file__)
par1_dir_fullname = os.path.abspath(os.path.join(file_fullname, os.pardir))
par2_dir_fullname = os.path.abspath(os.path.join(par1_dir_fullname, os.pardir))
sys.path.insert(0, par2_dir_fullname)

if __name__ == '__main__':
    run()
