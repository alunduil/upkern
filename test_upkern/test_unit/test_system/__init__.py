# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from upkern import system

from test_upkern.test_unit import TestBaseUnit


class TestRebuildModules(TestBaseUnit):
    def test_rebuild_modules(self):
        '''system.rebuild_modules()'''

        self.mock_helpers_emerge()

        system.rebuild_modules()

        self.mocked_helpers_emerge.assert_called_once_with(options = [ '-v' ], package = '@module-rebuild')
