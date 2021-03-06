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

"""Defines the model for the grub bootloader."""

import re
import datetime
import os
import shutil
import upkern.helpers as helpers

from upkern.bootloader.base import BaseBootLoader
from upkern.helpers import mountedboot

class Grub(BaseBootLoader):
    """A specific boot loader, GRUB, handler.

    Specifies the generic boot loader interface for the GRUB boot loader.

    """

    def __init__(self, debug = False, verbose = False, quiet = False,
            dry_run = False):
        """Set up GRUB specific information.

        Finalize the boot loader initialization with grub specific 
        information.

        """

        super(Grub, self).__init__(debug, verbose, quiet, dry_run)

    @property
    def configuration_uri(self):
        """The grub configuration URI."""
        return "/boot/grub/grub.conf"

    @property
    def grub_root(self):
        """The grub root parameter."""
        if not hasattr(self, "_grub_root"):
            match = re.match(r"/dev/[\w\d]+(?P<letter>\w)(?P<number>\d+)",
                    self.boot_partition)

            if self.arguments["debug"]:
                helpers.debug({
                    "self.boot_partition": self.boot_partition,
                    })

            self._grub_root = "(hd{letter!s},{number!s})".format(
                    letter = "abcdefghijklmnopqrstuvwxyz".find(
                        match.group("letter")),
                    number = -1 + int(match.group("number")))
        return self._grub_root

    @property
    @mountedboot
    def configuration(self):
        """The grub configuration file (mutable)."""
        if not hasattr(self, "_configuration"):
            configuration = open(self.configuration_uri, 'r')
            self._configuration = [
                    line.rstrip("\n") for line in configuration.readlines()
                    ]
            configuration.close()
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        """The grub configuration file (mutable)."""
        self._configuration = value

    @mountedboot
    def prepare(self, kernel = None, kernel_options = "", initrd = False):
        """Prepare the configuration file."""

        if not self.arguments["quiet"]:
            print("Preparing GRUB configuration ...")

        if not self._has_kernel(kernel.name):
            new_configuration = []

            options = []

            for line in self.configuration:
                if re.search("default", line, re.I):
                    new_configuration.append("".join([
                        "default {default!s}".format(
                            default = 1 + int(line.partition(" ")[2])),
                        ]))
                elif re.search("^[^#]*kernel", line, re.I):
                    new_configuration.append(line)

                    if self.arguments["debug"]:
                        helpers.debug({
                            "kernel_options": kernel_options,
                            "kernel_options.split(" ")": kernel_options.split(" "),
                            "type(kernel_options)": type(kernel_options),
                            })

                    options = [
                        option.strip() for option in line.split(" ") \
                                if not re.search("(?:kernel|/boot/|root=)",
                                    option, re.I)
                        ]

                    if self.arguments["debug"]:
                        helpers.debug({
                            "options": options,
                            "type(options)": type(options),
                            "len(kernel_options)": len(kernel_options),
                            })
                else:
                    new_configuration.append(line)

            if len(kernel_options):
                kernel_options = " ".join(list(set(
                    kernel_options.split(" ").extend(options))))
            else:
                kernel_options = " ".join(list(set(options)))

            kernel_options = kernel_options.lstrip(" ")

            if self.arguments["debug"]:
                helpers.debug({
                    "kernel_options": kernel_options,
                    })

            kernel_entry = [
                    "",
                    "# Kernel added {time!s}:".format(
                        time = datetime.datetime.now()),
                    "title={kernel_name}".format(kernel_name = kernel.name),
                    "  root {grub_root}".format(grub_root = self.grub_root),
                    "  kernel /boot/{image} root={root} {options}".format(
                        image = kernel.image, root = self.root_partition,
                        options = kernel_options),
                    ]


            if self.arguments["debug"]:
                helpers.debug({
                    "kernel_entry": kernel_entry,
                    })

            if initrd:
                kernel_entry.append(
                        "  initrd /boot/{initrd}".format(
                            initrd = kernel.initrd))

            new_configuration.extend(kernel_entry)

            self.configuration = new_configuration

            if not self.arguments["quiet"]:
                print("GRUB configuration prepared.")

    @mountedboot
    def install(self):
        """Install the configuration and make the system bootable."""

        if not self.arguments["quiet"]:
            print("Installing GRUB configuration.")

        if self.arguments["dry_run"]:
            dry_list = [
                    "cp {config}{{,.bak}}".format(
                        config = self.configuration_uri),
                    "cat > {config}".format(config = self.configuration_uri),
                    "\n".join(self.configuration),
                    "^d",
                    "rm {config}.bak".format(config = self.configuration_uri),
                    ]
            helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            if os.access(self.configuration_uri, os.W_OK):
                try:
                    shutil.copy(self.configuration_uri, "{config}.bak".format(
                        config = self.configuration_uri))
                    configuration = open(self.configuration_uri, "w")
                    configuration.write("\n".join(self.configuration))
                    configuration.flush()
                    configuration.close()
                except Exception as error:
                    os.rename("{config}.bak".format(
                        config = self.configuration_uri),
                        self.configuration_uri)
                    raise error
                finally:
                    if os.access("{config}.bak".format(
                        config = self.configuration_uri), os.W_OK):
                        os.remove("{config}.bak".format(
                            config = self.configuration_uri))

        if not self.arguments["quiet"]:
            print("GRUB configuration installed.")

    def _has_kernel(self, kernel_name):
        """Return the truthness of the kernel's presence in the config."""
        return len([
            line for line in self.configuration if re.search(kernel_name, line)
            ])

