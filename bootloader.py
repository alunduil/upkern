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
import datetime
from string import ascii_lowercase
import shutil

from upkern_helpers import is_boot_mounted

class BootLoaderException(Exception):
    """Generic error class for a bootloader problem.

    Specifies an error condition in the bootloader module.

    """

    def __init__(self, message, *args):
        Exception.__init__(self, *args)
        self.message = message

    def print_message(self):
        print self.message

def create_bootloader(*args):
    """Factory method for getting the appropriate BootLoader object.

    Returns the correct BootLoader object for the system currently running.

    Post Conditions:
    We know the boot loader the system uses, and will now attempt to configure
    that boot loader exclusively and correctly.

    Returns:
    The correct BootLoader child object.

    """

    expression = re.compile('^\[ebuild\s+(R|U)\s+\].+$')

    for boot_loader in ("grub", "lilo", "silo"):
        output = os.popen('emerge -p ' + boot_loader + \
            ' 2>/dev/null | tail -n1', 'r')
        if expression.match(output.readline()):
            break;
    if boot_loader == "grub":
        return GRUB(*args)
    elif boot_loader == "lilo":
        return LILO(*args)
    elif boot_loader == "silo":
        return SILO(*args)
    else:
        raise BootLoaderException(
            "Could not determine the boot loader on this system!")

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

    def __init__(self, kernel, kernel_options = "", initrd = "",
        splash_theme = "", root_partition = ""):
        """Create a bootloader with generic options.

        Returns a generic bootloader with options that are common to all set
        appropriately for the machine run on.

        """

        self._kernel_image = kernel.image
        self._kernel_name = kernel.name

        if len(root_partition) > 0:
            self._root_partition = root_partition
        else:
            self._root_partition = self.__determine_root()

        self._kernel_options = kernel_options
        self._initrd = initrd
        self._splash_theme = splash_theme

        self._boot_partition = self.__determine_boot()

    def __determine_root(self):
        """Determine the root partition of the machine.

        Return the full device path to the root partition of the machine we
        are currently running on.

        """

        expression = re.compile('^(/dev/[a-z0-9/]+)\W+/\W+.+$', re.IGNORECASE)

        if os.access('/etc/fstab', os.F_OK):
            fstab = open('/etc/fstab', 'r')
            for line in fstab:
                if expression.match(line):
                    root_partition = expression.match(line).group(1)
                    fstab.close()
                    break
            else:
                output_list = [
                    "Root device name not found! Please, check that your",
                    " /etc/fstab file is formatted properly."
                    ]
                fstab.close()
                raise BootLoaderException(''.join(output_list));
        else:
            raise BootLoaderException("Cannot read from /etc/fstab!");
        return root_partition

    def __determine_boot(self):
        """Determine the boot partition of the machine.

        Return the full device path to the boot partition of the machine. Pass
        back the root partition if there is no separate boot partition.

        """

        expression = re.compile('^(?P<device>/dev/.+?)\s+/boot\s+.+$', \
            re.IGNORECASE)

        if os.access('/etc/fstab', os.F_OK):
            fstab = open('/etc/fstab', 'r')
            for line in fstab:
                if expression.match(line):
                    return expression.match(line).group("device")
            else:
                if is_boot_mounted():
                    return self.__root_partition
                else:
                    output_list = [
                        "Could not determine the device that /boot is",
                        " located on!"
                        ]
                    raise BootLoaderException(''.join(output_list))
        else:
            raise BootLoaderException("Could not access /etc/fstab!")

    def _has_kernel(self, config_location):
        """Determine if the boot loader's config already contains the kernel.

        Return true if the kernel we are interested in is already in the
        configuration file for the boot loader, and false if not.

        """

        if is_boot_mounted():
            expression = re.compile('^.+' + self._kernel_image + '\s+.+$')

            if os.access(config_location, os.F_OK):
                configuration = open(config_location, 'r')
            else:
                output_list = [
                    "Could not open the configuration file for the boot",
                    " loader!"
                    ]
                raise BootLoaderException(''.join(output_list), \
                    config_location)
            for line in configuration:
                if expression.match(line):
                    configuration.close()
                    return True
            configuration.close()
            return False
        else:
            os.system('mount /boot')
            self._has_kernel()
            os.system('umount /boot')

class GRUB(BootLoader):
    """A specific boot loader, GRUB, handler.

    Specifies the generic boot loader interface for the GRUB boot loader.

    boot_loader = create_bootloader()

    """

    def __init__(self, kernel, kernel_options = "", initrd = "", \
        splash_theme = "", root_partition = ""):
        """Set up GRUB specific information.

        Finalize the boot loader initialization with grub specific information.

        """

        BootLoader.__init__(self, kernel, kernel_options, initrd, \
            splash_theme, root_partition)

        self.__config_location = '/boot/grub/grub.conf'

        self.config = self.__config_location

        kernel_list = [
            "\n# Kernel added on " + datetime.date.today().ctime() + ":\n",
            "title=" + self._kernel_name + "\n",
            "\troot " + self.__determine_grub_root() + "\n",
            "\tkernel /boot/" + self._kernel_image + " root=" + self._root_partition,
            " " + self._kernel_options + " " + self._splash_theme
            ]
        self.__kernel_string = ''.join(kernel_list)
        if len(self._initrd) > 0:
            self.__kernel_string += "\n" + self._initrd
        self.__kernel_string += "\n"

    def create_configuration(self):
        """Create a new configuration file for the boot loader.

        Create a new configuration file in a temporary location for the boot
        loader. We'll use <normal location>.tmp as it should be pretty
        obvious that it is not meant to stick around.

        """

        if is_boot_mounted():
            if not self._has_kernel(self.__config_location):
                if os.access(self.__config_location, os.F_OK):
                    old_configuration = open(self.__config_location, 'r')
                    new_configuration = open(self.__config_location + '.tmp', \
                        'w')

                    expression = re.compile(
                        '^(default\s+)(?P<kernel_number>\d+)\s*$')

                    for line in old_configuration:
                        match = expression.match(line)
                        if match:
                            new_configuration.write(match.group(1) + \
                                str(int(match.group("kernel_number")) + 1) + \
                                "\n")
                        else:
                            new_configuration.write(line)

                    new_configuration.write(self.__kernel_string)

                    old_configuration.close()
                    new_configuration.close()

            else:
                shutil.copy(self.__config_location, self.__config_location + \
                    '.tmp')

        else:
            os.system('mount /boot')
            self.create_configuration()
            os.system('umount /boot')

    def __determine_grub_root(self):
        """Get the root as grub needs it.

        Return the (hd0,0) style string for the boot partition that grub has
        come to use.

        """

        expression = re.compile(
            '/dev/.d(?P<drive_letter>.)(?P<part_number>\d+)')
        match = expression.match(self._boot_partition)
        if match:
            return "(hd" + \
                str(ascii_lowercase.find(match.group('drive_letter'))) \
                + "," + str(int(match.group('part_number')) - 1) + ")"

        expression = re.compile(
            '/dev/cciss/c0d(?P<drive_number>\d+)p(?P<part_number>\d+)')
        match = expression.match(self._boot_partition)
        if match:
            return "(hd" + \
                str(ascii_lowercase.find(match.group('drive_number'))) \
                + "," + str(match.group('part_number')) + ")"

        raise BootLoaderException("Couldn't determine the grub root string!",
            self._boot_partition)

    def install_configuration(self):
        """Install the newly created configuration file.


        Install the tmp config file into the actual location.

        """

        if is_boot_mounted():
            if os.access(self.__config_location + '.tmp', os.F_OK):
                shutil.move(self.__config_location + '.tmp',
                    self.__config_location)
        else:
            os.system('mount /boot')
            self.install_configuration()
            os.system('umount /boot')

class SILO(BootLoader):
    """A specific bootloader, SILO, handler.

    Specifies the generic bootloader interface for the SILO bootloader.

    boot_loader = create_bootloader()

    """

    def __init__(self, kernel, kernel_options = "", initrd = "", \
        splash_theme = "", root_partition = ""):
        """Set up SILO specific information.

        Prepare the bootloader to be ready to install a SILO configuration
        file, and write a new one in place.

        """

        BootLoader.__init__(self, kernel, kernel_options, initrd, \
            splash_theme, root_partition)

        self.__config_location = '/etc/silo.conf'

        self.config = self.__config_location

        kernel_list = [
            "\n# Kernel added on " + datetime.date.today().ctime() + ":\n",
            "image = /boot/" + self._kernel_image + "\n",
            "\tlabel = " + self._kernel_name + "\n"
            ]
        self.__kernel_string = ''.join(kernel_list)

    def create_configuration(self):
        """Create a new configuration file for the bootloader.

        Create a temporary config file in the same location as the real
        file that is ready to be installed.

        """

        if is_boot_mounted():
            if not self._has_kernel(self.__config_location):
                if os.access(self.__config_location, os.F_OK):
                    old_configuration = open(self.__config_location, 'r')
                    new_configuration = open(self.__config_location + '.tmp', \
                        'w')

                    matched = False
                    expression = re.compile('image\s*=\s*.+$')

                    for line in old_configuration:
                        if expression.match(line) and not matched:
                            new_configuration.write(self.__kernel_string)
                            matched = True
                        new_configuration.write(line)

                    old_configuration.close()
                    new_configuration.close()

            else:
                shutil.copy(self.__config_location, self.__config_location + \
                    '.tmp')

        else:
            os.system('mount /boot')
            self.create_configuration()
            os.system('umount /boot')

    def install_configuration(self):
        """Install the newly created configuration file.

        Overwrite the existing configuration with the one that has our new
        kernel entry in it.

        """

        if is_boot_mounted():
            if os.access(self.__config_location + '.tmp', os.F_OK):
                shutil.move(self.__config_location + '.tmp',
                    self.__config_location)
                if self._boot_partition != self._root_partition:
                    shutil.copy(self.__config_location,
                        '/boot')
                    os.system('/sbin/silo -C /boot/silo.conf')
                else:
                    os.system('/sbin/silo')
        else:
            os.system('mount /boot')
            self.install_configuration()
            os.system('umount /boot')
