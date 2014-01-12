# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

from upkern.arguments import ARGUMENTS
from upkern.bootloaders import BootLoader
from upkern.initramfs import InitialRAMFileSystem
from upkern.sources import Sources
from upkern.system import rebuild_modules

def run():
    '''Main execution function for upkern.'''

    p = ARGUMENTS.parse_args()

    logging.basicConfig(level = getattr(logging, p.level.upper()))

    sources = Sources(name = p.name)

    sources.emerge(force = p.force)

    sources.prepare(configuration = p.configuration)
    sources.configure(configurator = p.configurator, accept_defaults = p.yes)

    if p.time:
        start = datetime.datetime.now()

    sources.build()

    if p.time:
        delta = datetime.datetime.now() - start

    if p.module_rebuild:
        rebuild_modules()

    sources.install()

    initramfs = None

    if p.initramfs:
        initramfs = InitialRAMFileSystem(p.initramfs_preparer)
        initramfs.configure(*p.initramfs_options)

        initramfs.build()

        initramfs.install()

    bootloader = Bootloader()
    bootloader.configure(sources = sources, kernel_options = p.kernel_options, initramfs = initramfs)

    bootloader.build()

    bootloader.install()

    logger.info(
            'The kernel, %s, has been successfully installed.  Please, check ' \
            'that all configuration files are installed correctly and the ' \
            'bootloader is configured correctly',
            sources.binary_name
            )

    if p.time:
        logger.info('The kernel\'s build time was %s', str(delta))
