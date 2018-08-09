# -*- coding: utf-8 -*-
from __future__ import absolute_import

from setuptools import find_packages, setup

import parse_1c_build

setup(
    name='parse_1c_build',
    version=parse_1c_build.__version__,
    description='Parse and build utilities for 1C:Enterprise',
    author='Cujoko',
    author_email='cujoko@gmail.com',
    url='https://github.com/Cujoko/parse-1c-build',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ],
    keywords='1c parse build v8reader v8unpack gcomp',
    entry_points={
        'console_scripts': [
            'p1cb=parse_1c_build.__main__:run'
        ]
    },
    license='MIT',
    dependency_links=[
        'https://gitlab.com/Cujoko/commons/-/archive/master/commons-master.tar.gz#egg=commons-2.0.0',
        'https://gitlab.com/Cujoko/commons-1c/-/archive/master/commons-1c-master.tar.gz#egg=commons_1c-2.0.0'
    ],
    install_requires=[
        'commons>=2.0.0',
        'commons-1c>=2.0.0',
        'six>=1.11.0'
    ]
)
