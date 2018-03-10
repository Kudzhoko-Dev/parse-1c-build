# -*- coding: utf-8 -*-
from setuptools import setup

import parse_1c_build

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
        'Programming Language :: Python :: 3.6',

        'Topic :: Software Development',
        'Topic :: Utilities'
    ],

    keywords='1c parse build v8reader v8unpack gcomp',

    install_requires=[
        'commons',
        'commons-1c'
    ],

    dependency_links=[
        'http://github.com/Cujoko/commons/tarball/master',
        'http://github.com/Cujoko/commons-1c/tarball/master'
    ],

    py_modules=['parse_1c_build'],

    entry_points={
        'console_scripts': [
            'p1cb=parse_1c_build.__main__:run'
        ]
    }
)
