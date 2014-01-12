# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock

from upkern.initramfs import genkernel

from test_upkern.test_common.test_initramfs.test_genkernel import TestBaseGenKernelPreparer
from test_upkern.test_unit import TestBaseUnit


class TestGenKernelPreparerMethods(TestBaseGenKernelPreparer, TestBaseUnit):
    mocks_mask = TestBaseUnit.mocks_mask
    mocks = TestBaseUnit.mocks

    mocks.add('GenKernel.options')
    def mock_options(self, options = ''):
        if 'GenKernel.options' in self.mocks_mask:
            return

        _ = mock.patch.object(genkernel.GenKernelPreparer, 'options', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_options = _.start()
        mocked_options.return_value = options

    def test_build_without_options(self):
        '''initramfs.genkernel.GenKernelPreparer().build()—without options'''

        self.mock_subprocess_call()
        self.mock_options()

        self.prepare_preparer()

        self.p.build()

        command = 'genkernel --no-ramdisk-modules initramfs'
        self.mocked_subprocess_call.assert_called_once_with(command, shell = True)

    def test_build_with_options(self):
        '''initramfs.genkernel.GenKernelPreparer().build()—with options'''

        self.mock_subprocess_call()
        self.mock_options('--lvm --mdadm')

        self.prepare_preparer()

        self.p.build()

        command = 'genkernel --no-ramdisk-modules --lvm --mdadm initramfs'
        self.mocked_subprocess_call.assert_called_once_with(command, shell = True)
