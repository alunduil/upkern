# -*- coding: utf-8 -*-

# Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>            
#                                                                      
# This program is free software; you can redistribute it andor modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.                                  
#                                                                      
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.                         
#                                                                      
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.            

class BaseBootLoader(object):
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

    def __init__(self, debug = False, verbose = False, quiet = False,
            dry_run = False):
        """Create a bootloader with generic options.

        Returns a generic bootloader with options that are common to 
        all set appropriately for the machine run on.

        """
        
        self.arguments = {
                "debug": debug,
                "verbose": verbose,
                "quiet": quiet,
                "dry_run": dry_run,
                "kernel_name": kernel_name,
                "kernel_options": kernel_options,
                }

    @property
    def root_partition(self):
        """Get the system's root partition."""
        return FSTab["/"]

    @property
    def boot_partition(self):
        """Get the system's boot partition."""
        if "/boot" in FSTab:
            return FSTab["/boot"]
        return FSTab["/"]

    @property
    def has_kernel(self):
        """Get whether this bootloader's configuration contains the kernel."""
        raise AttributeError("has_kernel")

    @property
    def configuration(self):
        """Get the configuration file for the bootloader (if applicable)."""
        raise AttributeError("configuration")

    def prepare(self, kernel = None, kernel_options = ""):
        """Prepare the configuration of the bootloader."""
        raise NotImplementedError("prepare")

    def install(self):
        """Install the configuration and make the system bootable."""
        raise NotImplementedError("install")

