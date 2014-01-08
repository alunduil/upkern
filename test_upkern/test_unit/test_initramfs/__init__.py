# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import unittest

from upkern import initramfs

logger = logging.getLogger(__name__)

class TestInitialRAMFileSystemConstructor(unittest.TestCase):
    def test_sources_genkernel(self):
        '''initramfs.InitialRAMFileSystem('genkernel')'''

        i = initramfs.InitialRAMFileSystem('genkernel')

        self.assertIsInstance(i.preparer, initramfs.genkernel.GenKernelPreparer)

    def test_sources_dracut(self):
        '''initramfs.InitialRAMFileSystem('dracut')'''

        i = initramfs.InitialRAMFileSystem('dracut')

        self.assertIsInstance(i.preparer, initramfs.dracut.DracutPreparer)
