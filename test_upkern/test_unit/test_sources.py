# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import mock
import unittest

from upkern import sources

from test_upkern.test_fixtures.test_sources import SOURCES

logger = logging.getLogger(__name__)

class TestKernelIndex(unittest.TestCase):
    def setUp(self):
        super(TestKernelIndex, self).setUp()

        self.kernel_strings = [ ( _['directory_name'], _['kernel_index'] ) for _ in SOURCES['all'] ]

    def test_kernel_index(self):
        for kernel_string, result in self.kernel_strings:
            self.assertEqual(result, sources.kernel_index(kernel_string))

class TestSourcesConstructor(unittest.TestCase):
    def test_sources_no_arguments(self):
        '''Sources()'''

        s = sources.Sources()

        self.assertIsNone(s.name)

    def test_sources_with_name(self):
        '''Sources(name = ?)'''

        for source in SOURCES['all']:
            s = sources.Sources(name = source['name'])

            self.assertEqual(source['name'], s.name)

class TestSourcesProperties(unittest.TestCase):
    def setUp(self):
        super(TestSourcesProperties, self).setUp()

    def mock_gentoolkit_helpers_fileowner(self, package_names):
        _ = mock.patch('upkern.sources.gentoolkit.helpers.FileOwner')

        self.addCleanup(_.stop)

        self.mocked_gentoolkit_helpers_fileowner = _.start()

        mocked_finder = mock.MagicMock()
        self.mocked_gentoolkit_helpers_fileowner.return_value = mocked_finder
        mocked_finder.side_effect = [ [ ( _, ) ] for _ in package_names ]

    def mock_package_name(self, package_name):
        _ = mock.patch.object(sources.Sources, 'package_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_package_name = _.start()
        mocked_package_name.return_value = package_name

    def mock_source_directories(self, source_directories):
        _ = mock.patch.object(sources.Sources, 'source_directories', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_source_directories = _.start()
        mocked_source_directories.return_value = source_directories

    def prepare_sources(self, name):
        self.s = sources.Sources(name = name)

    def test_directory_name(self):
        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_gentoolkit_helpers_fileowner(source['package_names'])
            self.mock_package_name(source['package_name'])
            self.mock_source_directories(source['source_directories'])

            self.prepare_sources(source['name'])

            self.assertEqual(source['directory_name'], self.s.directory_name)

            logger.info('finished testing %s', source['package_name'])
