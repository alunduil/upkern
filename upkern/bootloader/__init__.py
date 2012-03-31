# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>            
#                                                                      
# This program is free software; you can redistribute it andor modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.                                  
#                                                                      
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.                         
#                                                                      
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.            

from gentoolkit.helpers import get_installed_cpvs
from gentoolkit.cpv import split_cpv
from gentoolkit.package import Package

from bootloaders import Grub

def BootLoader(*args, **kargs):
    """Factory method for getting the appropriate BootLoader object.

    Returns the correct BootLoader object for the system currently running.

    """

    bootloaders = get_installed_cpvs(lambda x: x.startswith('sys-boot'))
    bootloaders = [ split_cpv(bootloader)[1] + Package(bootloader).environment["SLOT"] for bootloader in bootloaders ]

    if kargs["debug"]:
        helpers.debug({
            "bootloaders", bootloaders,
            })

    bootloaders = set(["grub0", "grub2"]) & set(bootloaders)

    if "grub" in bootloaders:
        return Grub(*args, **kargs)

