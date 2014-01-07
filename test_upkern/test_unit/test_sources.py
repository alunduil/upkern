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

from test_upkern.test_common.test_sources import TestBaseSources
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

    mocks.add('portage.config')
    def mock_portage_config(self, portage_configuration):
        if 'portage.config' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.portage.config')

        self.addCleanup(_.stop)

        self.mocked_portage_config = _.start()
        self.mocked_portage_config.return_value = portage_configuration

    mocks.add('Sources.source_directories')
    def mock_source_directories(self, source_directories):
        if 'Sources.source_directories' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'source_directories', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_source_directories = _.start()
        mocked_source_directories.return_value = source_directories

    mocks.add('helpers.mount')
    def mock_helpers_mount(self):
        if 'helpers.mount' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.helpers.mount')

        self.addCleanup(_.stop)

        self.mocked_helpers_mount = _.start()

    mocks.add('helpers.unmount')
    def mock_helpers_unmount(self):
        if 'helpers.unmount' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.helpers.unmount')

        self.addCleanup(_.stop)

        self.mocked_helpers_unmount = _.start()

    def test_configuration_files(self):
        '''sources.Sources().configuration_files'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            _ = copy.copy(source['configuration_files'])
            random.shuffle(_)
            self.mock_os_listdir(_)
            self.mock_helpers_mount()
            self.mock_helpers_unmount()

            self.prepare_sources(source['name'])

            self.assertEqual(source['configuration_files'], self.s.configuration_files)

            logger.info('finished testing %s', source['package_name'])

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

    mocks.add('gentoolkit.query.Query')
    def mock_gentoolkit_query_find_installed(self, package_names):
        if 'gentoolkit.query.Query' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.gentoolkit.query.Query')

        self.addCleanup(_.stop)

        self.mocked_gentoolkit_query = _.start()

        self.mocked_query = mock.MagicMock()
        self.mocked_gentoolkit_query.return_value = self.mocked_query
        self.mocked_query.return_value = package_names

    mocks.add('subprocess.call')
    def mock_subprocess_call(self, result = 0):
        if 'subprocess.call' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.subprocess.call')

        self.addCleanup(_.stop)

        self.mocked_subprocess_call = _.start()
        self.mocked_subprocess_call.return_value = result

    mocks.add('Sources.portage_configuration')
    def mock_portage_configuration(self, portage_configuration):
        if 'Sources.portage_configuration' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'portage_configuration', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_portage_configuration = _.start()
        mocked_portage_configuration.return_value = portage_configuration

    mocks.add('helpers.emerge')
    def mock_helpers_emerge(self):
        if 'helpers.emerge' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.helpers.emerge')

        self.addCleanup(_.stop)

        self.mocked_helpers_emerge = _.start()

    def test_source_build(self):
        '''sources.Sources().build()'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_portage_configuration(source['portage_configuration'])
            self.mock_subprocess_call()

            self.prepare_sources(source['name'])

            self.s.build()

            command = 'make {0} && make {0} modules_install'.format(source['portage_configuration']['MAKEOPTS'])
            self.mocked_subprocess_call.called_once_with(command, shell = True)

    def _configure_wrapper(self, command, *args, **kwargs):
        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.mock_portage_configuration(source['portage_configuration'])
            self.mock_subprocess_call()

            self.prepare_sources(source['name'])

            self.s.configure(*args, **kwargs)

            command = command.format(source['portage_configuration']['MAKEOPTS'])
            self.mocked_subprocess_call.called_once_with(command, shell = True)

    def test_configure(self):
        '''sources.Sources().configure()'''

        self._configure_wrapper('make {0} menuconfig')

    def test_configure_with_configurator(self):
        '''sources.Sources().configure(configurator = ?)'''

        for configurator in [ 'menuconfig', 'oldconfig', 'silentoldconfig' ]:
            self._configure_wrapper('make {{0}} {0}'.format(configurator), configurator = configurator)

    def test_configure_with_accept_defaults(self):
        '''sources.Sources().configure(accept_defaults = True)'''

        self._configure_wrapper('yes "" | make {0} menuconfig', accept_defaults = True)

    def _install_wrapper(self, installed, called = True):
        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            if installed:
                self.mock_gentoolkit_query_find_installed([ source['package_name'] ])
            else:
                self.mock_gentoolkit_query_find_installed([])

            self.mock_helpers_emerge()
            self.mock_package_name(source['package_name'])

            self.prepare_sources(source['name'])

            self.s.install()

            logger.debug('self.mocked_helpers_emerge.calls: %s', self.mocked_helpers_emerge.calls)

            if called:
                self.mocked_helpers_emerge.called_once_with(options = [ '-n', '-1', '-v' ], package = source['package_name'])
            else:
                self.assertFalse(self.mocked_helpers_emerge.called)

    def test_install_installed(self):
        '''sources.Sources().install()—installed'''

        self._install_wrapper(installed = True, called = False)

    def test_install_not_installed(self):
        '''sources.Sources().install()—not installed'''

        self._install_wrapper(installed = False)

    def test_install_with_force_installed(self):
        '''sources.Sources().install(force = True)—installed'''

        self._install_wrapper(installed = True)

    def test_install_with_force_not_installed(self):
        '''sources.Sources().install(force = True)—not installed'''

        self._install_wrapper(installed = False)

logger.debug('TestSourcesMethod.mocks: %s', TestSourcesMethod.mocks)
