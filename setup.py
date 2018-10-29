# -*- coding: utf-8 -*-
from __future__ import absolute_import

import codecs
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with codecs.open(os.path.join(here, 'parse_1c_build', '__about__.py'), 'r', 'utf-8') as f:
    exec (f.read(), about)

setup(
    name='parse_1c_build',
    version=about['__version__'],
    description='Parse and build utilities for 1C:Enterprise',
    author='Cujoko',
    author_email='cujoko@gmail.com',
    url='https://gitlab.com/Cujoko/parse-1c-build',
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
    install_requires=[
        'commons @ https://gitlab.com/Cujoko/commons/-/archive/master/commons-master.tar.gz',
        'commons-1c @ https://gitlab.com/Cujoko/commons-1c/-/archive/master/commons-1c-master.tar.gz',
        'six>=1.11.0'
    ]
)
