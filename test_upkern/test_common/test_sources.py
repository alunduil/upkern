# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock
import unittest

from upkern import sources


class TestBaseSources(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

    mocks.add('Sources.configuration_files')
    def mock_configuration_files(self, configuration_files):
        if 'Sources.configuration_files' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'configuration_files', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_configuration_files = _.start()
        mocked_configuration_files.return_value = configuration_files

    mocks.add('Sources.directory_name')
    def mock_directory_name(self, directory_name):
        if 'Sources.directory_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'directory_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_directory_name = _.start()
        mocked_directory_name.return_value = directory_name

    mocks.add('Sources.kernel_suffix')
    def mock_kernel_suffix(self, kernel_suffix):
        if 'Sources.kernel_suffix' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'kernel_suffix', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_kernel_suffix = _.start()
        mocked_kernel_suffix.return_value = kernel_suffix

    mocks.add('Sources.package_name')
    def mock_package_name(self, package_name):
        if 'Sources.package_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'package_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_package_name = _.start()
        mocked_package_name.return_value = package_name

    mocks.add('system.utilties.mount')
    def mock_system_utilities_mount(self):
        if 'system.utiltiies.mount' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.system.utilities.mount')

        self.addCleanup(_.stop)

        self.mocked_system_utilities_mount = _.start()

    mocks.add('system.utilities.unmount')
    def mock_system_utilities_unmount(self):
        if 'system.utilities.unmount' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.system.utilities.unmount')

        self.addCleanup(_.stop)

        self.mocked_system_utilities_unmount = _.start()

    def prepare_sources(self, *args, **kwargs):
        self.s = sources.Sources(*args, **kwargs)
