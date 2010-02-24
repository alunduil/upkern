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

        kernel_list = [
            "\n# Kernel added on ", str(datetime.datetime.now()), ":\n",
            "title=", self._kernel.get_name(), "\n",
            "  root ", self._get_grub_root(), "\n",
            "  kernel /boot/", self._kernel.get_image(), "-",
            self._kernel.get_suffix(), " root=", self._root_partition,
            " ", kernel_options
            ]
        kernel_string = "".join(kernel_list)

        if self._debug:
            output.debug(__file__, {'kernel_string':kernel_string})

        self._kernel_string = kernel_string

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
            kernel_expr = re.compile("kernel.*?root=[\w\d/]+\s+(.+?)\s*")
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
                    kernel_options = kernel.group(1)
                    if self._debug:
                        output.debug(__file__, 
                            {"kernel_options":kernel_options})
                else:
                    tmp_configuration.append(line)

            tmp_configuration.append(self._kernel_string + kernel_options)

            if self._debug:
                for line in tmp_configuration:
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
                self.create_configuration()
                os.system('umount /boot')
        else:
            if self._dry_run: pass
            else: pass
            pass

