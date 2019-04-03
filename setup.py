# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import setup

here = Path(__file__).parent

about = {}
with Path(here, 'parse_1c_build', '__about__.py').open() as f:
    exec(f.read(), about)

setup(
    name='parse-1c-build',
    version=about['__version__'],
    description='Parse and build utilities for 1C:Enterprise',
    author='Cujoko',
    author_email='cujoko@gmail.com',
    url='https://github.com/Cujoko/parse-1c-build',
    packages=['parse_1c_build'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Russian',
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
        'cjk-commons>=3.3.0',
        'commons-1c>=3.1.0'
    ]
)
