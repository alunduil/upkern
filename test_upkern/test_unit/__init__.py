# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import mock
import unittest

logger = logging.getLogger(__name__)


class TestBaseUnit(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

    mocks.add('system.portage.emerge')
    def mock_system_portage_emerge(self):
        if 'system.portage.emerge' in self.mocks_mask:
            return

        module_name = self.__module__.replace('test_', '').replace('.unit', '').split('.')
        module_name.extend([ 'system', 'portage', 'emerge' ])

        known_symbols = set()
        module_name = '.'.join([ _ for _ in module_name if _ not in known_symbols and not known_symbols.add(_) ])

        logger.debug('module_name: %s', module_name)

        _ = mock.patch(module_name)

        self.addCleanup(_.stop)

        self.mocked_system_portage_emerge = _.start()

    mocks.add('subprocess.call')
    def mock_subprocess_call(self, result = 0):
        if 'subprocess.call' in self.mocks_mask:
            return

        _ = mock.patch(self.__module__.replace('test_', '').replace('.unit', '') + '.subprocess.call')

        self.addCleanup(_.stop)

        self.mocked_subprocess_call = _.start()
        self.mocked_subprocess_call.return_value = result
