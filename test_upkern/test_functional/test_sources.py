# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import mock
import os
import shutil

from upkern import sources

from test_upkern.test_common.test_sources import TestBaseSources
from test_upkern.test_fixtures.test_sources import SOURCES
from test_upkern.test_functional import TestBaseFunctional

logger = logging.getLogger(__name__)

ORIGINALS = {
    'os.path.islink': os.path.islink,
    'os.path.lexists': os.path.lexists,
    'os.readlink': os.readlink,
    'os.rename': os.rename,
    'os.remove': os.remove,
    'os.symlink': os.symlink,
    'shutil.copy': shutil.copy,
    'shutil.move': shutil.move,
}


class TestFunctionalSources(TestBaseSources, TestBaseFunctional):
    mocks_mask = set().union(TestBaseSources.mocks_mask, TestBaseFunctional.mocks_mask)
    mocks = set().union(TestBaseSources.mocks, TestBaseFunctional.mocks)

    def wrap_os_path_lexists(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.path.lexists'](path)

        _ = mock.patch('upkern.sources.os.path.lexists')

        self.addCleanup(_.stop)

        self.wrapped_os_path_lexists = _.start()
        self.wrapped_os_path_lexists.side_effect = wrapped

    def wrap_os_remove(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.remove'](path)

        _ = mock.patch('upkern.sources.os.remove')

        self.addCleanup(_.stop)

        self.wrapped_os_remove = _.start()
        self.wrapped_os_remove.side_effect = wrapped

    def wrap_shutil_copy(self, prefix):
        def wrapped(src, dst):
            src = os.path.normpath(prefix + '/' + src)
            dst = os.path.normpath(prefix + '/' + dst)
            return ORIGINALS['shutil.copy'](src, dst)

        _ = mock.patch('upkern.sources.shutil.copy')

        self.addCleanup(_.stop)

        self.wrapped_shutil_copy = _.start()
        self.wrapped_shutil_copy.side_effect = wrapped

    def actual_contents(self, path):
        real_path = os.path.normpath(self.temporary_directory_path + '/' + path)

        _ = None

        with open(real_path, 'r') as fh:
            _ = fh.read()

        logger.debug('contents: %s', _)

        return _


class TestSourcesCopyConfiguration(TestFunctionalSources):
    mocks_mask = TestFunctionalSources.mocks_mask
    mocks = TestFunctionalSources.mocks

    def populate_temporary_directory_files(self, items = {}):
        items.update({
            '/usr/src/linux': [ '.config' ],
        })

        super(TestSourcesCopyConfiguration, self).populate_temporary_directory_files(items)

    def wrap_shutil_move(self, prefix):
        def wrapped(src, dst):
            src = os.path.normpath(prefix + '/' + src)
            dst = os.path.normpath(prefix + '/' + dst)
            return ORIGINALS['shutil.move'](src, dst)

        _ = mock.patch('upkern.sources.shutil.move')

        self.addCleanup(_.stop)

        self.wrapped_shutil_move = _.start()
        self.wrapped_shutil_move.side_effect = wrapped

    def test_copy_configuration_without_configuration_files(self):
        '''sources.Sources()._copy_configuration()—without configuration files'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files()

            self.mock_configuration_files([])

            self.wrap_os_path_lexists(self.temporary_directory_path)
            self.wrap_os_remove(self.temporary_directory_path)
            self.wrap_shutil_copy(self.temporary_directory_path)
            self.wrap_shutil_move(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s._copy_configuration()

            self.assertEqual(1, self.recursive_file_count('/'))

            self.assertEqual(
                self.expected_contents['/usr/src/linux/.config'],
                self.actual_contents('/usr/src/linux/.config')
            )

            logger.info('finished testing %s', source['package_name'])

    def test_copy_configuration_with_configuration_files(self):
        '''sources.Sources()._copy_configuration()—with configuration files'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files({
                '/boot': source['configuration_files'],
            })

            self.mock_configuration_files(source['configuration_files'])
            self.mock_system_utilities_mount()
            self.mock_system_utilities_unmount()

            self.wrap_os_path_lexists(self.temporary_directory_path)
            self.wrap_os_remove(self.temporary_directory_path)
            self.wrap_shutil_copy(self.temporary_directory_path)
            self.wrap_shutil_move(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s._copy_configuration()

            self.assertEqual(len(source['configuration_files']) + 1, self.recursive_file_count('/'))

            self.assertEqual(
                self.expected_contents[os.path.join(os.path.sep, 'boot', source['configuration_files'][0])],
                self.actual_contents('/usr/src/linux/.config')
            )

            logger.info('finished testing %s', source['package_name'])

    def test_copy_configuration_specific_without_configuration_files(self):
        '''sources.Sources()._copy_configuration(configuration = '/boot/config-3.12.6-gentoo')—with configuration files'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            _ = [ 'config-3.12.6-gentoo', ]

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files({ '/boot': _, })

            self.mock_configuration_files(_)
            self.mock_system_utilities_mount()
            self.mock_system_utilities_unmount()

            self.wrap_os_path_lexists(self.temporary_directory_path)
            self.wrap_os_remove(self.temporary_directory_path)
            self.wrap_shutil_copy(self.temporary_directory_path)
            self.wrap_shutil_move(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s._copy_configuration(configuration = '/boot/config-3.12.6-gentoo')

            self.assertEqual(2, self.recursive_file_count('/'))

            self.assertEqual(
                self.expected_contents['/boot/config-3.12.6-gentoo'],
                self.actual_contents('/usr/src/linux/.config')
            )

            logger.info('finished testing %s', source['package_name'])


class TestSourcesSetupSymlink(TestFunctionalSources):
    mocks_mask = TestFunctionalSources.mocks_mask
    mocks = TestFunctionalSources.mocks

    def populate_temporary_directory_symlinks(self, items = {}):
        for directory_path, symlinks in items.items():
            for name, target in symlinks.items():
                name_path = os.path.join(directory_path, name)
                logger.debug('link name: %s', name_path)

                target_path = os.path.join(directory_path, target)
                target_path = os.path.relpath(target_path, os.path.dirname(os.path.commonprefix([ target_path, name_path ])))
                logger.debug('target: %s', target_path)

                real_name_path = os.path.normpath( self.temporary_directory_path + name_path)
                logger.debug('real link name: %s', real_name_path)

                if not os.path.exists(os.path.dirname(real_name_path)):
                    os.makedirs(os.path.dirname(real_name_path))

                ORIGINALS['os.symlink'](target_path, real_name_path)

    def wrap_os_path_islink(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.path.islink'](path)

        _ = mock.patch('upkern.sources.os.path.islink')

        self.addCleanup(_.stop)

        self.wrapped_os_path_islink = _.start()
        self.wrapped_os_path_islink.side_effect = wrapped

    def wrap_os_readlink(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.readlink'](path)

        _ = mock.patch('upkern.sources.os.readlink')

        self.addCleanup(_.stop)

        self.wrapped_os_readlink = _.start()
        self.wrapped_os_readlink.side_effect = wrapped

    def wrap_os_symlink(self, prefix):
        def wrapped(source, link_name):
            if source.startswith('/'):
                source = os.path.normpath(prefix + '/' + source)
            link_name = os.path.normpath(prefix + '/' + link_name)
            return ORIGINALS['os.symlink'](source, link_name)

        _ = mock.patch('upkern.sources.os.symlink')

        self.addCleanup(_.stop)

        self.wrapped_os_symlink = _.start()
        self.wrapped_os_symlink.side_effect = wrapped

    def read_symlink(self, path):
        path = os.path.normpath(self.temporary_directory_path + '/' + path)

        return ORIGINALS['os.readlink'](path)

    def test_setup_symlink_without_link(self):
        '''sources.Sources()._setup_symlink()—without link'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            _ = 'linux-3.12.6-gentoo'

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files({ '/usr/src': [ _ ] })

            self.mock_directory_name(_)

            self.wrap_os_path_islink(self.temporary_directory_path)
            self.wrap_os_symlink(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s._setup_symlink()

            self.assertEqual(_, self.read_symlink('/usr/src/linux'))

            logger.info('finished testing %s', source['package_name'])

    def test_setup_symlink_with_link(self):
        '''sources.Sources()._setup_symlink()—with link'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files({ '/usr/src': source['source_directories'] })
            self.populate_temporary_directory_symlinks({ '/usr/src': { 'linux': source['source_directories'][-1] } })

            self.mock_directory_name(source['source_directories'][0])

            self.wrap_os_path_islink(self.temporary_directory_path)
            self.wrap_os_readlink(self.temporary_directory_path)
            self.wrap_os_remove(self.temporary_directory_path)
            self.wrap_os_symlink(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s._setup_symlink()

            self.assertEqual(source['source_directories'][0], self.read_symlink('/usr/src/linux'))

            logger.info('finished testing %s', source['package_name'])


class TestSourcesInstall(TestFunctionalSources):
    mocks_mask = TestFunctionalSources.mocks_mask
    mocks = TestFunctionalSources.mocks

    mocks.add('Sources.binary_name')
    def mock_binary_name(self, binary_name):
        if 'Sources.binary_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'binary_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_binary_name = _.start()
        mocked_binary_name.return_value = binary_name

    def wrap_os_rename(self, prefix):
        def wrapped(src, dst):
            if src.startswith('/'):
                src = os.path.normpath(prefix + '/' + src)
            dst = os.path.normpath(prefix + '/' + dst)
            return ORIGINALS['os.rename'](src, dst)

        _ = mock.patch('upkern.sources.os.rename')

        self.addCleanup(_.stop)

        self.wrapped_os_rename = _.start()
        self.wrapped_os_rename.side_effect = wrapped

    def test_install(self):
        '''sources.Sources().install()'''

        for source in SOURCES['all']:
            logger.info('testing %s', source['package_name'])

            self.prepare_temporary_directory()
            self.populate_temporary_directory_files(
                {
                    '/boot': [
                        '.keep',
                    ],
                    '/usr/src/linux': [
                        '.config',
                        'System.map',
                    ],
                    '/usr/src/linux/arch/x86_64/boot': [
                        'bzImage',
                    ],
                }
            )

            self.mock_kernel_suffix(source['kernel_suffix'])
            self.mock_system_utilities_mount()
            self.mock_system_utilities_unmount()

            self.wrap_os_path_lexists(self.temporary_directory_path)
            self.wrap_os_rename(self.temporary_directory_path)
            self.wrap_shutil_copy(self.temporary_directory_path)

            self.prepare_sources(source['name'])

            self.s.install()

            self.assertEqual(
                self.expected_contents['/usr/src/linux/.config'],
                self.actual_contents('/boot/{0}'.format(source['configuration_name'])),
            )

            logger.info('finished testing %s', source['package_name'])
