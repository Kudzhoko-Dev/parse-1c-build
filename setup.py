#! python3
# -*- coding: utf-8 -*-
import decompiler1cwrapper
from setuptools import setup


setup(
    name='decompiler1cwrapper',
    version=decompiler1cwrapper.__version__,

    author='Cujoko',
    author_email='cujoko@gmail.com',

    py_modules=['decompiler1cwrapper'],

    entry_points={
        'console_scripts': [
            'decompile1c=decompiler1cwrapper:decompile',
            'compile1c=decompiler1cwrapper:compile_'
        ]
    }
)
