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

import re
import os
import upkern.helpers as helpers

from upkern.bootloader.base import BaseBootLoader
from upkern.helpers import mountedboot
from upkern.system import FSTab

def mountedgrub(func):
    """A decorator that checks if boot is mounted before running the function.

    If boot is not mounted; it gets mounted and unmounted properly.

    """

    def new_func(*args, **kargs):
        """Closure definition."""
        if FSTab()["/boot/grub2"] and os.path.ismount("/boot/grub2"):
            res = func(*args, **kargs)
        else:
            os.system('mount /boot/grub2')
            try:
                res = func(*args, **kargs)
            except Exception as error:
                raise error
            finally:
                os.system('umount /boot/grub2')
        return res
    return new_func

class Grub2(BaseBootLoader):
    """A specific boot loader, GRUB, handler.

    Specifies the generic boot loader interface for the GRUB boot loader.

    """

    def __init__(self, debug = False, verbose = False, quiet = False,
            dry_run = False):
        """Set up GRUB specific information.

        Finalize the boot loader initialization with grub specific 
        information.

        """

        super(Grub2, self).__init__(debug, verbose, quiet, dry_run)

    @property
    def configuration_uri(self):
        """The grub configuration URI."""
        return "/boot/grub2/grub.cfg"

    @property
    def grub_defaults_uri(self):
        """The grub defaults configuration URI."""
        return "/etc/default/grub"

    @property
    def configuration(self):
        """The grub configuration file (mutable)."""
        if not hasattr(self, "_configuration"):
            configuration = open(self.configuration_uri, 'r')
            self._configuration = [ line.rstrip("\n") for line in configuration.readlines() ]
            configuration.close()
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        """The grub configuration file (mutable)."""
        self.configuration = value

    @mountedboot
    def prepare(self, kernel = None, kernel_options = ""):
        """Prepare the configuration file."""

        grub_image = "kernel" + "".join(kernel.image.partition("-")[1:])

        if self.arguments["dry_run"]:
            dry_list = [
                    "pushd /boot",
                    "ln -s {kernel_image} {grub_image}".format(grub_image = grub_image, kernel_image = kernel.image),
                    "popd",
                    # TODO find a better way to depict this ...
                    "sed -i -e 's/(GRUB_CMDLINE_LINUX_DEFAULT=\")(.*)(\")/\\0\\1 {kernel_options}\\3/' {defaults}".format(kernel_options = kernel_options, defaults = self.grub_defaults_uri),
                    ]
            helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            original_pwd = os.getcwd()
            os.chdir("/boot")
            if not os.path.islink(grub_image):
                os.symlink(kernel.image, grub_image)
            os.chdir(original_pwd)

            new_grub_defaults = []

            for line in open(self.grub_defaults_uri, "r").readlines():
                if re.search(r"GRUB_CMDLINE_LINUX_DEFAULT", line):
                    line = line[:-1] + " " + kernel_options + "\""
                    new_grub_defaults.extend(line)
                else:
                    new_grub_defaults.extend(line)

            grub_defaults = open(self.grub_defaults_uri, "w")
            grub_defaults.write("\n".join(new_grub_defaults))
            grub_defaults.flush()
            grub_defaults.close()

    @mountedgrub
    @mountedboot
    def install(self):
        """Install the configuration and make the system bootable."""
        if self.arguments["dry_run"]:
           dry_list = [
                   "cp {grub_config}{{.,bak}}".format(grub_config = self.configuration_uri),
                   "grub2-mkconfig -o {grub_config}".format(grub_config = self.configuration_uri),
                   "rm {grub_config}.bak".format(grub_config = self.configuration_uri),
                   ]
           helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            try:
                shutil.copy(self.configuration_uri, "{grub_config}.bak".format(grub_config = self.configuration_uri))
                status = subprocess.call("grub2-mkconfig -o {grub_config}".format(grub_config = self.configuration_uri), shell = True)
                if status != 0:
                    pass # TODO raise an appropriate error

            except Exception as error:
                os.rename("{grub_config}.bak".format(grub_config = self.configuration_uri), self.configuration_uri)
                raise error
            finally:
                if os.access("{grub_config}.bak".format(grub_config = self.configuration_uri), os.W_OK):
                    os.remove("{grub_config}.bak".format(grub_config = self.configuration_uri))

