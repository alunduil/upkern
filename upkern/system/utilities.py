# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
import subprocess


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
        raise RuntimeError('mount encountered an error')

    return True


def unmount(mountpoint):
    '''Unmount the specified location.

    .. note::
        This unconditionally unmounts the specified mountpoint.

    '''

    command = 'umount {0}'.format(mountpoint)
    status = subprocess.call(command, shell = True)

    if status != 0:
        raise RuntimeError('umount encountered an error')
