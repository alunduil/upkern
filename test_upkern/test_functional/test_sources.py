# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import functools
import logging
import mock
import os
import shutil
import tempfile
import uuid

from upkern import sources

from test_upkern.test_common.test_sources import TestBaseSources
from test_upkern.test_fixtures.test_sources import SOURCES

logger = logging.getLogger(__name__)

ORIGINALS = {
        'os.path.islink': os.path.islink,
        'os.path.lexists': os.path.lexists,
        'os.readlink': os.readlink,
        'os.remove': os.remove,
        'os.symlink': os.symlink,
        'shutil.copy': shutil.copy,
        'shutil.move': shutil.move,
        }

class TestFunctionalSources(TestBaseSources):
    mocks_mask = TestBaseSources.mocks_mask
    mocks = TestBaseSources.mocks

    def prepare_temporary_directory(self):
        self.temporary_directory_path = tempfile.mkdtemp(prefix = 'test_', suffix = '_upkern')

        logger.debug('self.temporary_directory_path: %s', self.temporary_directory_path)

        self.addCleanup(functools.partial(shutil.rmtree, self.temporary_directory_path))

    def populate_temporary_directory_files(self, items = {}):
        self.expected_contents = {}

        for directory_path, file_names in items.items():
            for file_name in file_names:
                file_path = os.path.join(directory_path, file_name)
                logger.debug('file_path: %s', file_path)

                real_file_path = os.path.normpath(self.temporary_directory_path + file_path)
                logger.debug('real_file_path: %s', real_file_path)

                _ = uuid.uuid4()
                self.expected_contents[file_path] = str(_)

                if not os.path.exists(os.path.dirname(real_file_path)):
                    os.makedirs(os.path.dirname(real_file_path))

                with open(real_file_path, 'w') as fh:
                    fh.write(str(_))

    def wrap_os_remove(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.remove'](path)

        _ = mock.patch('upkern.sources.os.remove')

        self.addCleanup(_.stop)

        self.wrapped_os_remove = _.start()
        self.wrapped_os_remove.side_effect = wrapped

class TestSourcesCopyConfiguration(TestFunctionalSources):
    mocks_mask = TestFunctionalSources.mocks_mask
    mocks = TestFunctionalSources.mocks

    def populate_temporary_directory_files(self, items = {}):
        items.update({
            '/usr/src/linux': [ '.config' ],
            })

        super(TestSourcesCopyConfiguration, self).populate_temporary_directory_files(items)

    def wrap_os_path_lexists(self, prefix):
        def wrapped(path):
            path = os.path.normpath(prefix + '/' + path)
            return ORIGINALS['os.path.lexists'](path)

        _ = mock.patch('upkern.sources.os.path.lexists')

        self.addCleanup(_.stop)

        self.wrapped_os_path_lexists = _.start()
        self.wrapped_os_path_lexists.side_effect = wrapped

    def wrap_shutil_copy(self, prefix):
        def wrapped(src, dst):
            src = os.path.normpath(prefix + '/' + src)
            dst = os.path.normpath(prefix + '/' + dst)
            return ORIGINALS['shutil.copy'](src, dst)

        _ = mock.patch('upkern.sources.shutil.copy')

        self.addCleanup(_.stop)

        self.wrapped_shutil_copy = _.start()
        self.wrapped_shutil_copy.side_effect = wrapped

    def wrap_shutil_move(self, prefix):
        def wrapped(src, dst):
            src = os.path.normpath(prefix + '/' + src)
            dst = os.path.normpath(prefix + '/' + dst)
            return ORIGINALS['shutil.move'](src, dst)

        _ = mock.patch('upkern.sources.shutil.move')

        self.addCleanup(_.stop)

        self.wrapped_shutil_move = _.start()
        self.wrapped_shutil_move.side_effect = wrapped

    def actual_contents(self, path):
        real_path = os.path.normpath(self.temporary_directory_path + '/' + path)

        _ = None

        with open(real_path, 'r') as fh:
            _ = fh.read()

        logger.debug('contents: %s', _)

        return _

    def recursive_file_count(self, path):
        logger.debug('path: %s', path)
        logger.debug('real path: %s', os.path.normpath(self.temporary_directory_path + '/' + path))

        return functools.reduce(lambda x, y: x + y, [ len(files) for root, directories, files in os.walk(os.path.normpath(self.temporary_directory_path + '/' + path)) ], 0)

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

logger.debug('TestSourcesCopyConfiguration.mocks: %s', TestSourcesCopyConfiguration.mocks)

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

    mocks.add('Sources.directory_name')
    def mock_directory_name(self, directory_name):
        if 'Sources.directory_name' in self.mocks_mask:
            return

        _ = mock.patch.object(sources.Sources, 'directory_name', mock.PropertyMock())

        self.addCleanup(_.stop)

        mocked_directory_name = _.start()
        mocked_directory_name.return_value = directory_name

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

logger.debug('TestSourcesSetupSymlink.mocks: %s', TestSourcesSetupSymlink.mocks)
