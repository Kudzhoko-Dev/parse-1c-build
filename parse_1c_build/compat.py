# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import PY2

if PY2:
    # noinspection PyUnresolvedReferences
    from pathlib2 import Path
else:
    # noinspection PyUnresolvedReferences,PyCompatibility
    from pathlib import Path
