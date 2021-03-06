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

"""Specifies the binary model for dealing with kernel objects."""

import os
import shutil
import re
import platform
import subprocess
import upkern.helpers as helpers

from gentoolkit.query import Query as GentoolkitQuery
from upkern.helpers import mountedboot

class Binary(object):
    """A kernel binary model.

    All references to how things should be called makes an attempt to coincide
    with the documentation provided in the relevant kernel sources.  If
    mismatches are discovered bugs should be reported to
    http://bugs.alunduil.com.  The reference sources will be those provided by
    the Gentoo Portage tree.

    See the following URL for a list of current kernel sources:
    http://packages.gentoo.org/packages/sys-kernel/gentoo-sources

    """

    def __init__(self, directory, debug = False, verbose = False, quiet = False,
            dry_run = False):
        """Returns a kernel binary object.

        Get the appropriate information about the system to know how to perform
        basic kernel actions.  Once the initial data discovery is complete
        (within this method), the normal sequence to build a kernel is the
        following:

        """

        self.arguments = {
                "directory": directory,
                "debug": debug,
                "verbose": verbose,
                "quiet": quiet,
                "dry_run": dry_run,
                }

    @property
    def name(self):
        """The name of the kernel for labelling purposes."""
        return self.arguments["directory"]

    @property
    def image(self):
        """The complete image name."""
        return self.install_image + self.suffix

    @property
    def initrd(self):
        """The complete initrd name."""
        return "initramfs" + self.suffix + ".img"

    @property
    def install_image(self):
        """Returns the name of the install image for this architecture.

        Return bzImage, vmlinux, etc depending on the arch of the machine.

        From the kernel README:

        Although originally developed first for 32-bit x86-based PCs (386 or
        higher), today Linux also runs on (at least) the Compaq Alpha AXP, Sun
        SPARC and UltraSPARC, Motorola 68000, PowerPC, PowerPC64, ARM, Hitachi
        SuperH, Cell, IBM S/390, MIPS, HP PA-RISC, Intel IA-64, DEC VAX, AMD
        x86-64, AXIS CRIS, Xtensa, AVR32 and Renesas M32R architectures.

        We will support more of these as we get accurate reports of what image
        is produced by the default make command.

        """

        if not hasattr(self, "_install_image"):
            self._install_image = {
                    "x86_64": "bzImage",
                    "i686": "bzImage",
                    }[platform.machine()]

        return self._install_image

    @property
    def image_directory(self):
        """The location inside the kernel sources of the resulting image.

        Caches the result after the first invocation so subsequent calls are
        quicker.

        """

        if not hasattr(self, "_image_directory"):
            self._image_directory = "arch/{arch}/boot/".format(
                    arch = re.sub(r"i\d86", "x86", platform.machine()))
        return self._image_directory

    @property
    def suffix(self):
        """The suffix of this kernel's name.

        e.g. -3.3.0-gentoo-r2

        Caches the result after the first invocation so subsequent calls are
        quicker.

        TODO Check that this is actually quicker with the caching.

        """

        if not hasattr(self, "_suffix"):
            self._suffix = "-" + self.arguments["directory"].partition("-")[2]
        return self._suffix

    @mountedboot
    def install(self):
        """Install the kernel into /boot.

        1. Go into the source directory.
        2. Copy the image file to /boot.
        3. Copy the config file to /boot
        4. Copy System.map to /boot.
        5. Copy System.map to /

        """

        if not self.arguments["quiet"]:
            print("Installing the kernel binaries ...")

        original_directory = os.getcwd()

        if self.arguments["dry_run"]:
            dry_list = [
                    "pushd /usr/src/linux",
                    "cp {directory}{image} /boot/{image}{suffix}".format(
                        directory = self.image_directory,
                        image = self.install_image, suffix = self.suffix),
                    "cp .config /boot/config{suffix}".format(
                        suffix = self.suffix),
                    "cp System.map /boot/System.map{suffix}".format(
                        suffix = self.suffix),
                    "cp System.map /System.map",
                    "popd",
                    ]
            helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            def undo():
                if os.access("/boot/{image}{suffix}".format(
                    image = self.install_image, suffix = self.suffix), os.W_OK):
                    os.remove("/boot/{image}{suffix}".format(
                        image = self.install_image, suffix = self.suffix))
                if os.access("/boot/config{suffix}".format(
                    suffix = self.suffix), os.W_OK):
                    os.remove("/boot/config{suffix}".format(
                        suffix = self.suffix))
                if os.access("/bot/System.map{suffix}".format(
                    suffix = self.suffix), os.W_OK):
                    os.remove("/boot/System.map{suffix}".format(
                        suffix = self.suffix))
                if os.access("/System.map", os.W_OK) and os.access(
                    "/System.map.bak", os.W_OK):
                    os.remove("/System.map")
                    os.rename("/System.map.bak", "/System.map")
            try:
                os.chdir("/usr/src/linux")
                shutil.copy("{directory}{image}".format(
                    directory = self.image_directory, image = self.install_image),
                    "/boot/{image}{suffix}".format(image = self.install_image,
                        suffix = self.suffix))
                shutil.copy(".config", "/boot/config{suffix}".format(
                    suffix = self.suffix))
                shutil.copy("System.map", "/boot/System.map{suffix}".format(
                    suffix = self.suffix))
                if os.access("/System.map", os.W_OK):
                    shutil.copy("/System.map", "/System.map.bak")
                shutil.copy("System.map", "/System.map")
                os.chdir(original_directory)
            except IOError as error:
                undo()
                raise IOError(error.errno, error.strerror, "/boot")
            except Exception as error:
                undo()
                raise error
            finally:
                if os.access("/System.map.bak", os.W_OK):
                    os.remove("/System.map.bak")

        if not self.arguments["quiet"]:
            print("Kernel binaries installed.")

    @mountedboot
    def install_initramfs(self, dracut_options = ""):
        """Build and install the initramfs using dracut."""

        if not self.arguments["quiet"]:
            print("Building and installing initramfs ...")

        if not len(GentoolkitQuery("sys-kernel/dracut").find_installed()):
            return

        if self.arguments["verbose"]:
            helpers.verbose("Building and Installing initramfs: True")

        command = [
                "dracut -H --force {options} /boot/{initrd} {suffix}".format(
                    options = dracut_options,
                    initrd = self.initrd,
                    suffix = self.suffix[1:]),
                ]

        if self.arguments["dry_run"]:
            helpers.colorize("GREEN", "".join(command))
        else:
            status = subprocess.call("".join(command), shell = True)
            if status != 0:
                pass # TODO raise an appropriate exception

        if not self.arguments["quiet"]:
            print("initramfs built and installed.")

