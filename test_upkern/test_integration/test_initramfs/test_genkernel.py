# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from test_upkern.test_common.test_initramfs.test_genkernel import TestBaseGenKernelPreparer


class TestGenKernelPreparerMethods(TestBaseGenKernelPreparer):
    mocks_mask = TestBaseGenKernelPreparer.mocks_mask
    mocks = TestBaseGenKernelPreparer.mocks

    def test_configure_without_parameters(self):
        '''initramfs.genkernel.GenKernelPreparer().configure()'''

        self.prepare_preparer()

        self.p.configure()

        self.assertEqual('', self.p.options)

    def test_configure_with_parameters(self):
        '''initramfs.genkernel.GenKernelPreparer().configure('lvm', 'mdraid')'''

        self.prepare_preparer()

        self.p.configure('lvm', 'mdadm')

        self.assertEqual('--lvm --mdadm', self.p.options)
