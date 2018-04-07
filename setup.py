# -*- coding: utf-8 -*-
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
    entry_points={
        'console_scripts': [
            'p1cb=parse_1c_build.__main__:run'
        ]
    }
)
