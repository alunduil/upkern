# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

BOOTLOADERS = {}

from upkern.bootloaders import *

def BootLoader(*args, **kwargs):
    '''Bootloader factory.

    Returns an instance of the first BootLoader class that matches an installed
    bootloader on the system.

    All arguments passed are proxied to the returned BootLoader implementation.

    '''

    installed_bootloaders = get_installed_cpvs(lambda _: _.startswith('sys-boot'))
    installed_bootloaders = [ split_cpv(bootloader)[1] + Package(_).environment('SLOT') for _ in installed_bootloaders ]

    logger.debug('installed_bootloaders: %s', installed_bootloaders)

    eligible_bootloaders = set(BOOTLOADERS.keys()) & set(installed_bootloaders)

    logger.debug('eligible_bootloaders: %s', eligible_bootloaders)

    bootloader = None

    try:
        bootloader = eligible_bootloaders.pop()(*args, **kwargs)
    except KeyError:
        pass

    logger.info('using %s as the bootloader', bootloader)

    return bootloader
