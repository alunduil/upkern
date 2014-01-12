# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import mock
import unittest


class TestBaseUnit(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

    mocks.add('subprocess.call')
    def mock_subprocess_call(self, result = 0):
        if 'subprocess.call' in self.mocks_mask:
            return

        _ = mock.patch('upkern.sources.subprocess.call')

        self.addCleanup(_.stop)

        self.mocked_subprocess_call = _.start()
        self.mocked_subprocess_call.return_value = result
