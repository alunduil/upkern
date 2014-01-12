# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import functools
import logging
import os
import shutil
import tempfile
import unittest
import uuid

logger = logging.getLogger(__name__)


class TestBaseFunctional(unittest.TestCase):
    mocks_mask = set()
    mocks = set()

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

    def recursive_file_count(self, path):
        logger.debug('path: %s', path)
        logger.debug('real path: %s', os.path.normpath(self.temporary_directory_path + '/' + path))

        return functools.reduce(lambda x, y: x + y, [ len(files) for root, directories, files in os.walk(os.path.normpath(self.temporary_directory_path + '/' + path)) ], 0)
