# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os

from upkern import helpers

logger = logging.getLogger(__name__)

PREPARERS = {}

helpers.load_all_modules(__name__, os.path.dirname(__file__))

class InitialRAMFileSystem(object):
    def __init__(self, preparer, *args, **kwargs):
        self.preparer = PREPARERS[preparer](*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.preparer, name)
