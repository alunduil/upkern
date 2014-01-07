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

    mocks.add('Sources.package_name')
    def mock_package_name(self, package_name):
        if 'Sources.package_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'package_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_package_name = _.start()
        mocked_package_name.return_value = package_name

    def prepare_sources(self, *args, **kwargs):
        self.s = sources.Sources(*args, **kwargs)

