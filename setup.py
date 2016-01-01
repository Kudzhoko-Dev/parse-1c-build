#! python3
# -*- coding: utf-8 -*-
import decompiler1cwrapper
from setuptools import setup


setup(
    name='decompiler1cwrapper',

    version=decompiler1cwrapper.__version__,

    description='Decompile and compile utilities for 1C:Enterprise',

    url='https://github.com/Cujoko/decompiler1cwrapper',

    author='Cujoko',
    author_email='cujoko@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Utilities',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5'
    ],

    keywords='1c v8reader v8unpack gcomp',

    py_modules=['decompiler1cwrapper'],

    entry_points={
        'console_scripts': [
            'decompile1c=decompiler1cwrapper:decompile',
            'compile1c=decompiler1cwrapper:compile_'
        ]
    }
)

