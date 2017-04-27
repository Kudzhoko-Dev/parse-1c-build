#! python3
# -*- coding: utf-8 -*-
import parse_1c_build
from setuptools import setup


setup(
    name='parse_1c_build',

    version=parse_1c_build.__version__,

    description='Parse and build utilities for 1C:Enterprise',

    url='https://github.com/Cujoko/parse-1c-build',

    author='Cujoko',
    author_email='cujoko@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: Russian',

        'Programming Language :: Python :: 3.5',

        'Topic :: Software Development',
        'Topic :: Utilities'
    ],

    keywords='1c parse build v8reader v8unpack gcomp',

    install_requires=[
        'appdirs'
    ],

    py_modules=['parse_1c_build'],

    entry_points={
        'console_scripts': [
            'parse-1c=parse_1c_build:parse',
            'build-1c=parse_1c_build:build'
        ]
    }
)