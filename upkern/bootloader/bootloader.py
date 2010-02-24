# -*- coding: utf-8 -*-
############################################################################
#    Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>             #
#                                                                          #
#    This program is free software; you can redistribute it and#or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 2 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

from grub import Grub

def BootLoader(*args):
    """Factory method for getting the appropriate BootLoader object.

    Returns the correct BootLoader object for the system currently running.

    @note Unkown behaviour if multiple bootloaders are installed.
    @todo Make this not a function that looks like a class but a class.

    Post Conditions:
    We know the boot loader the system uses, and will now attempt to 
    configure that boot loader exclusively and correctly.

    Returns:
    The correct BootLoader child object.

    """

    from gentoolkit.helpers import get_installed_cpvs
    p = lambda x: x.startswith('sys-boot')
    for package in get_installed_cpvs(p):
        boot_loader = package
        break
    else:
        raise BootLoaderException("No bootloader installed!")

    if boot_loader == "grub": return Grub(*args)
    error_list = [
        "The bootloader you have installed: %s is not supported by",
        "upkern.  If you would like support for this bootloader added",
        "please submit a bug report to http://bugzilla.alunduil.com.",
        "We will try to add support for the bootloader as fast as",
        "possible."
        ]
    raise BootLoaderException(" ".join(error_list))

class BootLoaderException(Exception):
    def __init__(self, message, *args):
        Exception.__init__(self, *args)
        self.message = message

    def get_message(self):
        return self.message

