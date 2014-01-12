# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest

from upkern.initramfs import genkernel


class TestBaseGenKernelPreparer(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

    def prepare_preparer(self, *args, **kwargs):
        self.p = genkernel.GenKernelPreparer(*args, **kwargs)
