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

"""Contains necessary classes and functions to work with the boot loader.

Will provide a BootLoader class, a factory function for creating a class of
type GRUB, LILO, or SILO as appropriate for the current machine being worked
on. Will also provide a generic bootloader exception class.

"""

import re
import os

class BootLoaderException(Exception):
    """Generic error class for a bootloader problem.

    Specifies an error condition in the bootloader module.

    """

    def __init__(self, message, *args):
        Exception.__init__(self, *args)
        self.message = message

    def print_message():
        print message

def create_bootloader():
    """Factory method for getting the appropriate BootLoader object.

    Returns the correct BootLoader object for the system currently running.

    Post Conditions:
    We know the boot loader the system uses, and will now attempt to configure
    that boot loader exclusively and correctly.

    Returns:
    The correct BootLoader child object.

    """

    expression = re.compile('^\[ebuild\s+R\s+\].+$')

    for boot_loader in ("grub", "lilo", "silo"):
        output = os.popen('emerge -p ' + boot_loader + ' 2>/dev/null | tail -n1', 'r')
        if expression.match(output.readline()):
            break;
    if boot_loader == "grub":
        return GRUB()
    elif boot_loader == "lilo":
        return LILO()
    elif boot_loader == "silo":
        return SILO()
    else:
        raise BootLoaderException("Could not determine the boot loader on this system!")

class BootLoader(object):
    """A boot loader handling object.

    Specifies an interface that allows the programmer to easily work with the
    different types of boot loader configurations. This interface should
    provide an identical interface for GRUB, LILO, and SILO. This allows a
    programmer to make much cleaner code for working with all three boot
    loaders.

    The configuration files created should be reveiwed for style, and any
    comments or suggestions on how to improve the layout of the boot loader
    configuration files should be e-mailed to the author.

    boot_loader = create_bootloader()

    """

    def __init__(self, kernel_name, root_partition = "", initrd = "",
        kernel_options = "", splash_theme = ""):
        # self.root_partition = root_partition if len(root_partition) > 0 else \
            determine_root()

    def determine_root(self):
        expression = re.compile('^(/dev/[a-z0-9/]+)\W+/\W+.+$', re.IGNORECASE)

        if os.access('/etc/fstab', os.F_OK):
            fstab = open('/etc/fstab', 'r')
            for line in fstab:
                if expression.match(line):
                    root_partition = expression.match(line).group(1)
                    break
            else:
                raise BootLoaderException("Root device name not found!\nPlease, check that your /etc/fstab file is formatted properly.");
            fstab.close()
        else:
            raise BootLoaderException("Cannot read from /etc/fstab!");
        return root_partition

class GRUB(BootLoader):
    """A specific boot loader, GRUB, handler.

    Specifies the generic boot loader interface for the GRUB boot loader.

    boot_loader = create_bootloader()

    """

    def __init__(self, kernel_name, root_partition, initrd = "", kernel_options = "", splash_theme = ""):
        BootLoader.__init__()
