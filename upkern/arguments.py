# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import argparse

from upkern import information

ARGUMENTS = argparse.ArgumentParser()

ARGUMENTS.add_argument('--version', action = 'version', version = information.VERSION)

ARGUMENTS.add_argument(
        '--level',
        default = 'info',
        help = \
                'Sets the output level (verbosity) of the application.  Uses ' \
                'the standard `logging` module; thus, the level\'s from ' \
                '`logging`.  Default: %(default)s'
        )

ARGUMENTS.add_argument(
        '--force',
        '-f',
        action = 'store_true',
        help = \
                'Force any actions that might otherwise block the requested ' \
                'tasks.'
        )

ARGUMENTS.add_argument(
        '--time',
        '-t',
        action = 'store_true',
        help = \
                'Time the kernel build.'
        )

ARGUMENTS.add_argument(
        '--yes',
        '-y',
        action = 'store_true',
        help = \
                'Uses `yes` to accept all defaults for new configuration ' \
                'items.'
        )

ARGUMENTS.add_argument(
        '--configuration',
        '-f',
        help = \
                'Specifies an existing kernel configuration to use in place ' \
                'of the default.'
        )

_CONFIGURATORS = [
        'config',
        'menuconfig',
        'nconfig',
        'xconfig',
        'gconfig',
        'oldconfig',
        'silentoldconfig',
        'defconfig',
        '${PLATFORM}_defconfig',
        'allyesconfig',
        'allmodconfig',
        'allnoconfig',
        'randconfig',
        ]

ARGUMENTS.add_argument(
        '--configurator',
        '-c',
        choices = _CONFIGURATORS,
        default = 'menuconfig',
        help = \
                'Specifies which configurator (kernel configuring ' \
                'application) should be used to configure the kernel.  The ' \
                'standard configurators are `config`, `menuconfig`, and ' \
                '`oldconfig` but other options are available.  Default: ' \
                '%(default)s'
        )

ARGUMENTS.add_argument(
        '--kernel-options',
        '-o',
        help = \
                'Literal options to be passed to the kernel by the bootloader.'
        )

ARGUMENTS.add_argument(
        '--module-rebuild',
        '-r',
        action = 'store_true',
        help = \
                'Runs `emerge @module-rebuild` after building the new kernel.'
        )

ARGUMENTS.add_argument(
        '--initial-ramdisk',
        '-i',
        action = 'store_true',
        help = \
                'Specifies that an initial ramdisk should be built and ' \
                'configured as well as the base kernel.'
        )

ARGUMENTS.add_argument(
        '--initial-ramdisk-type',
        choices = [ 'genkernel', 'dracut' ],
        default = 'genkernel',
        help = \
                'Specifies the mechanism to build an initial ramdisk with.  ' \
                'Default: %(default)s'
        )

ARGUMENTS.add_argument(
        '--initial-ramdisk-options',
        help = \
                'Literal options to be passed to the initial ramdisk mechanism.'
        )

ARGUMENTS.add_argument(
        'name',
        nargs = '?',
        help = \
                'The name (using ebuild CPV conventions) of the kernel ' \
                'sources to build.  Default: most current sources available'
        )
