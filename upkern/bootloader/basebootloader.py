# -*- coding: utf-8 -*-
########################################################################
# Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>            #
#                                                                      #
# This program is free software; you can redistribute it and#or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program; if not, write to the                        #
# Free Software Foundation, Inc.,                                      #
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.            #
########################################################################

import bootloader
import re
import os

from upkern import output

class BaseBootLoader():
    """A boot loader handling object.

    Specifies an interface that allows the programmer to easily work 
    with the different types of boot loader configurations. This 
    interface should provide an identical interface for GRUB, LILO, and
    SILO. This allows a programmer to make much cleaner code for 
    working with all three boot loaders.

    The configuration files created should be reveiwed for style, and 
    any comments or suggestions on how to improve the layout of the 
    boot loader configuration files should be e-mailed to the author.

    """

    def __init__(self, kernel, kernel_options = "", debug = False, 
        verbose = False, dry_run = False):
        """Create a bootloader with generic options.

        Returns a generic bootloader with options that are common to 
        all set appropriately for the machine run on.

        """
        self._debug = debug
        self._verbose = verbose
        self._dry_run = dry_run

        self._kernel = kernel
        self._root_partition = self._get_root_partition()
        self._boot_partition = self._get_boot_partition()
        self._kernel_options = kernel_options

    def _get_root_partition(self):
        """Get the root partition of the machine.

        Return the full device path to the root partition of the
        machine we are currenlty running on.

        """
        root = self._get_partition(r'^/dev/[\w\d/]+\s+/\s+.+$')
        root = root[0].expandtabs(1).partition(" ")[0]
        if self._debug: output.debug(__file__, {'root':root})
        if len(root) < 1: 
            raise bootloader.BootLoaderException("Could not determine root device")
        return root

    def _get_boot_partition(self):
        """Get the boot partition of the machine.

        Return the full device path to the boot partition of the
        machine we are currently running on.

        """
        boot = self._get_partition(r'^/dev/[\w\d/]+\s+/boot\s+.+$')
        boot = boot[0].expandtabs(1).partition(" ")[0]
        if self._debug: output.debug(__file__, {'boot':boot})
        if len(boot) < 0: return self._root_partition
        return boot
        
    def _get_partition(self, regex, flags = re.I):
        """Get the line from fstab that matches filter.

        """
        if not os.access('/etc/fstab', os.R_OK):
            raise BootLoaderException("Can't read /etc/fstab")

        fstab = open('/etc/fstab', 'r')
        lines = fstab.readlines()
        fstab.close()

        return filter(lambda x: re.match(regex, x, flags), lines)

    def _has_kernel(self):
        """Determine if the bootloader's configuration has the kernel.

        """
        raise UnboundLocalError('_has_kernel')

