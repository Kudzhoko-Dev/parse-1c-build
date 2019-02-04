# -*- coding: utf-8 -*-
import logging

# noinspection PyUnresolvedReferences
from parse_1c_build.__about__ import __version__
# noinspection PyUnresolvedReferences
from parse_1c_build.build import Builder
# noinspection PyUnresolvedReferences
from parse_1c_build.parse import Parser

# noinspection PyUnresolvedReferences
logging.getLogger().setLevel(logging.DEBUG)
logger: logging.Logger = logging.getLogger(__name__)
