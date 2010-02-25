# -*- coding: utf-8 -*-
#########################################################################
# Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>             #
#                                                                       #
# This program is free software; you can redistribute it and#or modify  #
# it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation; either version 2 of the License, or     #
# (at your option) any later version.                                   #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU General Public License for more details.                          #
#                                                                       #
# You should have received a copy of the GNU General Public License     #
# along with this program; if not, write to the                         #
# Free Software Foundation, Inc.,                                       #
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
#########################################################################

from basebootloader import BaseBootLoader
from upkern import output, helpers

import datetime
import re
import os

class Grub(BaseBootLoader):
    """A specific boot loader, GRUB, handler.

    Specifies the generic boot loader interface for the GRUB boot loader.

    """
    def __init__(self, kernel, kernel_options = "", debug = False, 
        verbose = False, dry_run = False):
        """Set up GRUB specific information.

        Finalize the boot loader initialization with grub specific 
        information.

        """
        BaseBootLoader.__init__(self, kernel, kernel_options, debug, 
            verbose, dry_run)

        self._config_url = '/boot/grub/grub.conf'
        self._configuration = []

        # @todo Some good way to do this?
        kernel_list = [
            "",
            "# Kernel added on " + str(datetime.datetime.now()) + ":",
            "title=" + self._kernel.get_name(),
            "  root " + self._get_grub_root(),
            "  kernel /boot/" + self._kernel.get_image() + \
            self._kernel.get_suffix() + " root=" + \
            self._root_partition
            ]
        self._kernel_string = kernel_list # @todo Fix this up.
        if len(kernel_options) > 0: 
            self._kernel_string[-1] += " " + kernel_options

    def _get_grub_root(self):
        """Using the root partition found we create a GRUB root string.

        """
        match = re.match('/dev/.d(?P<letter>\w)(?P<number>\d+)', 
            self._boot_partition)

        if not match: 
            raise BootLoaderException("Device %s not supported" % self._boot_partition)

        from string import ascii_lowercase
        return "(hd" + \
            str(ascii_lowercase.find(match.group("letter"))) + "," + \
            str(int(match.group("number")) - 1) + ")"

    def create_configuration(self):
        """Create a new configuration file for the boot loader.

        Create a new configuration file in a temporary location for the
        boot loader. We'll use <normal location>.tmp as it should be
        pretty obvious that it is not meant to stick around.

        """

        if not helpers.is_boot_mounted():
            if self._dry_run:
                output.verbose('mount /boot')
                output.error('--dry-run requires that you manually mount /boot')
                output.verbose('umount /boot')
            else:
                os.system('mount /boot')
                self.create_configuration()
                os.system('umount /boot')
        else:
            if not os.access(self._config_url, os.R_OK):
                raise BootLoaderException("Could not read %s" % self._config_url)

            c = open(self._config_url)
            self._configuration = c.readlines()
            c.close()

            if self._already_have_kernel(): 
                if self._verbose or self._dry_run:
                    output.verbose("Kernel entry already in %s" % self._config_url)
                return
           
            tmp_configuration = []
            kernel_options = ""
            default_expr = re.compile("(default\s+)(?P<number>\d+)\s*")
            kernel_expr = re.compile("\s*kernel.*?root=[\w\d/]+\s+(.+)")
            for line in self._configuration:
                default = default_expr.match(line)
                kernel = kernel_expr.match(line)
                if default:
                    new_line_list = [
                        default.group(1), 
                        str(int(default.group("number")) + 1)
                        ]
                    if self._debug:
                        output.debug(__file__, 
                            {"default_line":"".join(new_line_list)})
                    tmp_configuration.append("".join(new_line_list))
                elif kernel:
                    tmp_configuration.append(line.rstrip())
                    kernel_options = kernel.group(1).rstrip()
                    if self._debug:
                        output.debug(__file__, 
                            {"kernel_options":kernel_options})
                else:
                    tmp_configuration.append(line.rstrip())

            self._kernel_string[-1] += " " + kernel_options

            if self._debug:
                for line in tmp_configuration:
                    output.debug(__file__, {"line":line})

            if self._debug:
                for line in self._kernel_string:
                    output.debug(__file__, {"line":line})

            self._configuration = tmp_configuration

    def _already_have_kernel(self):
        """Determine if our new kernel is already listed.

        """
        results = filter(lambda x: re.search(self._kernel.get_name(), x), self._configuration)
        if len(results) > 0: return True
        return False

    def install_configuration(self):
        """Install the newly created configuration file.


        Install the tmp config file into the actual location.

        """

        if self._already_have_kernel(): return

        if not helpers.is_boot_mounted():
            if self._dry_run:
                output.verbose('mount /boot')
                output.error('--dry-run requires that you manually mount /boot')
                output.verbose('umount /boot')
            else:
                os.system('mount /boot')
                self.install_configuration()
                os.system('umount /boot')
        else:
            self._configuration.extend(self._kernel_string)

            if self._dry_run:
                output.verbose("echo -en \n%s\n > /boot/grub/grub.conf" % "\n".join(self._configuration))
            else:
                if not os.access(self._config_url, os.W_OK):
                    raise BootLoaderException("Cannot write to /boot/grub/grub.conf")
                c = open(self._config_url, 'w')
                c.write("\n".join(self._configuration))
                c.flush()
                c.close()

