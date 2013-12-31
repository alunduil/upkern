# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import unittest

from upkern import sources

from test_upkern.test_fixtures.test_sources import SOURCES

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
