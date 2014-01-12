# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import os
import subprocess

logger = logging.getLogger(__name__)


def emerge(package, options = None):
    '''Wrapper for portage's emerge functionality.

    This method is just a wrapper for de-coupling purposes.  The implementation
    is malleable and reusable.

    .. note::
        This causes a critical (application stopping) error if not run as root.

    '''

    command = 'emerge'

    if options is not None:
        command += ' ' + ' '.join(options)

    command += ' ' + package

    logger.debug('command: %s', command)

    if os.getuid() != 0:
        raise PermissionError('emerge requires root permissions')
    else:
        status = subprocess.call(command, shell = True)

        if status != 0:
            pass  # TODO raise an appropriate exception
