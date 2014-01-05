# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import copy
import logging
import mock
import random
import unittest

from upkern import sources

from test_upkern.test_fixtures.test_sources import SOURCES

logger = logging.getLogger(__name__)

class TestKernelIndex(unittest.TestCase):
    def setUp(self):
        super(TestKernelIndex, self).setUp()

        self.kernel_strings = [ ( _['directory_name'], _['kernel_index'] ) for _ in SOURCES['all'] ]

    def test_kernel_index(self):
        '''sources.kernel_index()'''

        for kernel_string, result in self.kernel_strings:
            self.assertEqual(result, sources.kernel_index(kernel_string))

class TestSourcesConstructor(unittest.TestCase):
    def test_sources_no_arguments(self):
        '''sources.Sources()'''

        s = sources.Sources()

        self.assertIsNone(s.name)

    def test_sources_with_name(self):
        '''sources.Sources(name = ?)'''

        for source in SOURCES['all']:
            s = sources.Sources(name = source['name'])

            self.assertEqual(source['name'], s.name)

class TestBaseSources(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

    mocks.add('portage.config')
    def mock_portage_config(self, portage_configuration):
        if 'portage.config' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.portage.config')

        self.addCleanup(_.stop)

        self.mocked_portage_config = _.start()
        self.mocked_portage_config.return_value = portage_configuration

    def prepare_sources(self, name):
        self.s = sources.Sources(name = name)

class TestSourcesProperties(TestBaseSources):
    mocks_mask = TestBaseSources.mocks_mask
    mocks = TestBaseSources.mocks

    mocks.add('gentoolkit.helpers.FileOwner')
    def mock_gentoolkit_helpers_fileowner(self, package_names):
        if 'gentoolkit.helpers.FileOwner' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.gentoolkit.helpers.FileOwner')

        self.addCleanup(_.stop)

        self.mocked_gentoolkit_helpers_fileowner = _.start()

        self.mocked_finder = mock.MagicMock()
        self.mocked_gentoolkit_helpers_fileowner.return_value = self.mocked_finder
        self.mocked_finder.side_effect = [ [ ( _, ) ] for _ in package_names ]

    mocks.add('os.listdir')
    def mock_os_listdir(self, source_directories):
        if 'os.listdir' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.os.listdir')

        self.addCleanup(_.stop)

        self.mocked_os_listdir = _.start()
        self.mocked_os_listdir.return_value = source_directories

    mocks.add('Sources.package_name')
    def mock_package_name(self, package_name):
        if 'Sources.package_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'package_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_package_name = _.start()
        mocked_package_name.return_value = package_name

    mocks.add('Sources.source_directories')
    def mock_source_directories(self, source_directories):
        if 'Sources.source_directories' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'source_directories', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_source_directories = _.start()
        mocked_source_directories.return_value = source_directories

    def test_directory_name(self):
        '''sources.Sources().directory_name'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_gentoolkit_helpers_fileowner(source['package_names'])
            self.mock_package_name(source['package_name'])
            self.mock_source_directories(source['source_directories'])

            self.prepare_sources(source['name'])

            self.assertEqual(source['directory_name'], self.s.directory_name)

            logger.info('finished testing %s', source['package_name'])

    def test_package_name(self):
        '''sources.Sources().package_name'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_gentoolkit_helpers_fileowner(source['package_names'])
            self.mock_source_directories(source['source_directories'])

            self.prepare_sources(source['name'])

            self.assertEqual(source['package_name'], self.s.package_name)

            logger.info('finished testing %s', source['package_name'])

    def test_portage_configuration(self):
        '''sources.Sources().portage_configuration'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_portage_config(source['portage_configuration'])

            self.prepare_sources(source['name'])

            self.assertEqual(source['portage_configuration'], self.s.portage_configuration)

            logger.info('finished testing %s', source['package_name'])

    def test_source_directories(self):
        '''sources.Sources().source_directories'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            logger.debug('source[source_directories]: %s', source['source_directories'])

            _ = copy.copy(source['source_directories'])
            random.shuffle(_)
            self.mock_os_listdir(_)

            self.prepare_sources(source['name'])

            self.assertEqual(source['source_directories'], self.s.source_directories)

            logger.info('finished testing %s', source['package_name'])

logger.debug('TestSourcesProperties.mocks: %s', TestSourcesProperties.mocks)

class TestSourcesMethod(TestBaseSources):
    mocks_mask = TestBaseSources.mocks_mask
    mocks = TestBaseSources.mocks

    mocks.add('subprocess.call')
    def mock_subprocess_call(self, result = 0):
        if 'subprocess.call' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.subprocess.call')

        self.addCleanup(_.stop)

        self.mocked_subprocess_call = _.start()
        self.mocked_subprocess_call.return_value = result

    def test_source_build(self):
        '''sources.Sources().build()'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_portage_config(source['portage_configuration'])
            self.mock_subprocess_call()

            self.prepare_sources(source['name'])

            self.s.build()

            command = 'make {0} && make {0} modules_install'.format(source['portage_configuration']['MAKEOPTS'])
            self.mocked_subprocess_call.called_once_with(command, shell = True)

logger.debug('TestSourcesMethod.mocks: %s', TestSourcesMethod.mocks)
