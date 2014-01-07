# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

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
            pass # TODO raise an appropriate exception

def mount(mountpoint):
    '''Mount the specified location unless it's already mounted.

    In the typical idempotent fashion, this mounts the specified location unless
    it's already mounted.

    .. note::
        This assumes the mountpoint is defined in `/etc/fstab` and if not found
        there, it will throw an error.

    Returns
    -------

    True if the location was mounted; otherwise, False.

    '''

    if os.path.ismount(mountpoint):
        return False

    command = 'mount {0}'.format(mountpoint)
    status = subprocess.call(command, shell = True)

    if status != 0:
        pass # TODO raise an appropriate exception

    return True

def unmount(mountpoint):
    '''Unmount the specified location.

    .. note::
        This unconditionally unmounts the specified mountpoint.

    '''

    command = 'umount {0}'.format(mountpoint)
    status = subprocess.call(command, shell = True)

    if status != 0:
        pass # TODO raise an appropriate exception
