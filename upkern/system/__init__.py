# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from upkern import helpers

logger = logging.getLogger(__name__)


def rebuild_modules():
    '''Use emerge to rebuild all portage installed kernel modules.

    Basically, a wrapper for `emerge @module-rebuild`.

    '''

    logger.info('rebuilding portage installed kernel modules')

    options = []

    if logger.level < 30:
        options.append('-v')
    else:
        options.append('-q')

    helpers.emerge(options = options, package = '@module-rebuild')

    logger.info('finished rebuilding portage installed kernel modules')
