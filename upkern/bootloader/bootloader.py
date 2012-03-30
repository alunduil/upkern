# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>             
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

def BootLoader(*args):
    """Factory method for getting the appropriate BootLoader object.

    Returns the correct BootLoader object for the system currently running.

    """

    
    p = lambda x: x.startswith('sys-boot')
    for package in get_installed_cpvs(p):
        boot_loader = package
        break
    else:
        raise BootLoaderException("No bootloader installed!")

    from gentoolkit.cpv import split_cpv
    boot_loader = split_cpv(boot_loader)[1]

    if boot_loader == "grub": return Grub(*args)
    error_list = [
        "The bootloader you have installed: %s is not supported by",
        "upkern.  If you would like support for this bootloader added",
        "please submit a bug report to http://bugzilla.alunduil.com.",
        "We will try to add support for the bootloader as fast as",
        "possible."
        ]
    raise BootLoaderException(" ".join(error_list) % boot_loader)

class BootLoaderException(Exception):
    def __init__(self, message, *args):
        Exception.__init__(self, *args)
        self.message = message

    def get_message(self):
        return self.message

