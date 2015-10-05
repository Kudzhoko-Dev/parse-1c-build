#! python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os.path import join, dirname

import decompiler1cwrapper


setup(
    name='decompiler1cwrapper',
    version=decompiler1cwrapper.__version__,
    packages=find_packages(),

    author='Cujoko',
    author_email='cujoko@gmail.com'
)