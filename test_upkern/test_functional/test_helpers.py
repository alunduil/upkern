# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock

from upkern import helpers

from test_upkern.test_functional import TestBaseFunctional


class TestFunctionalLoadAllModules(TestBaseFunctional):
    mocks_mask = TestBaseFunctional.mocks_mask
    mocks = TestBaseFunctional.mocks

    mocks.add('importlib.import_module')
    def mock_importlib_import_module(self):
        if 'importlib.import_module' in self.mocks_mask:
            return

        _ = mock.patch('upkern.helpers.importlib.import_module')

        self.addCleanup(_.stop)

        self.mocked_importlib_import_module = _.start()

    def test_load_all_modules_empty(self):
        '''helpers.load_all_modules('foo', TEMPDIR)—empty directory'''

        self.prepare_temporary_directory()

        self.mock_importlib_import_module()

        helpers.load_all_modules('foo', self.temporary_directory_path)

        self.assertEqual(0, self.recursive_file_count('/'))

        self.assertFalse(self.mocked_importlib_import_module.called)

    def test_load_all_modules_flat(self):
        '''helpers.load_all_modules('foo', TEMPDIR)—flat directory'''

        self.prepare_temporary_directory()

        self.populate_temporary_directory_files(
            {
                '/foo': [
                    'a.py',
                    'b.py',
                    'c.py',
                ],
            }
        )

        self.mock_importlib_import_module()

        helpers.load_all_modules('foo', self.temporary_directory_path)

        self.assertEqual(3, self.recursive_file_count('/'))

        _ = [
            mock.call('foo.c'),
            mock.call('foo.b'),
            mock.call('foo.a'),
        ]
        self.mocked_importlib_import_module.assert_has_calls(_)
