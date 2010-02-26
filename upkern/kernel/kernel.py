# -*- coding: utf-8 -*-

########################################################################
# Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>            #
#                                                                      #
# This program is free software; you can redistribute it and#or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program; if not, write to the                        #
# Free Software Foundation, Inc.,                                      #
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.            #
########################################################################

import portage
import re
import platform
import os
import shutil

from upkern import output, helpers

class Kernel:
    """A kernel handler object.

    Specifies an interface that allows the programmer to easily work
    with the kernel sources that the object gets bound to. This allows 
    easy building, installing, and general manipulation of a kernel
    source directory. 

    All references to how things should be called make an attempt to 
    coincide with the documentation provided in the relevant kernel
    sources. This interface will attempt to stay in touch with the most
    recent kernel sources provided by the Gentoo Portage tree.

    See the following URL for a list of current kernels:
    http://packages.gentoo.org/package/sys-kernel/gentoo-sources

    kernel = Kernel(kernelName, sources, rebuildModules, buildMethod)

    """

    def __init__(self, configurator = "menuconfig", kernel_name = "",
        rebuild_modules = True, configuration = "", debug = False, 
        verbose = False, dry_run = False):
        """Returns a Kernel object with properly initialized data.

        Get the necessary information about the system to know how to
        perform basic kernel actions. We should be ready to configure,
        build, and install the kernel when this call completes.

        Post Conditions:
        The Kernel object is initialized, and the information has been
        populated.

        Returns:
        A Kernel object.

        """

        self._debug = debug
        self._verbose = verbose
        self._dry_run = dry_run
        self._configurator = configurator

        if self._verbose: 
            output.verbose("Configurator: %s", self._configurator)

        output.status("Getting information about kernel (this could take a while) ...")

        self._directory_name, self._emerge_name = \
            self._get_kernel_names(kernel_name)

        if self._verbose:
            output.verbose("Directory Name: %s", self._directory_name)
            output.verbose("Package Name: %s", self._emerge_name)

        self._install_image = self._get_install_image()
        self._suffix = "-" + self._directory_name.partition('-')[2]

        if self._verbose:
            output.verbose("Install Image: %s", self._install_image)

        self._rebuild_modules = False
        if rebuild_modules and self._have_module_rebuild():
            self._rebuild_modules = rebuild_modules

        if self._verbose:
            output.verbose("Rebuild Modules: %s", self._rebuild_modules)

        if not self._dry_run and os.getuid() != 0:
            raise KernelException("Insufficient priveleges to continue!")

        if self._dry_run: self._dry_set_symlink()
        else: self._set_symlink()

        if self._dry_run: self._dry_copy_config()
        else: self._copy_config()

        self._emerge_config = portage.config()

    def get_name(self):
        """Get the kernel name to put in the bootloader.

        """
        return self._directory_name

    def get_image(self):
        """Get the kernel image.

        """
        return self._install_image

    def get_suffix(self):
        """Get the suffix for the kernel.

        """
        return self._suffix

    def _copy_config(self):
        """Copy the configuration file into the source.

        @todo Make this function take a parameter (the file to copy
        into the source directory).

        Currently, this copies the highest versioned config file from
        /boot.

        """
        if not helpers.is_boot_mounted():
            os.system('mount /boot')
            self._copy_config() # @todo Update params.
            os.system('umount /boot')
        else:
            config_list = os.listdir('/boot')
            config_list = filter(lambda x: re.match('config-.+', x), 
                config_list)
            config_list.sort()
            if len(config_list) > 0:
                shutil.copy('/boot/' + config_list[-1], 
                    '/usr/src/linux/.config')

    def _dry_copy_config(self):
        """Dry run of _copy_config.

        """
        if not helpers.is_boot_mounted():
            output.verbose("mount /boot")
            output.error("--dry-run requires that you manually mount /boot")
            output.verbose("umount /boot")
        else:
            config_list = os.listdir('/boot')
            config_list = filter(lambda x: re.match('config-.+', x),
                config_list)
            config_list.sort()
            if len(config_list) > 0:
                output.verbose("cp /boot/%s /usr/src/linux/.config", 
                    config_list[-1])

    def _set_symlink(self):
        """Sets the symlink to the new kernel directory.

        """
        if os.path.islink('/usr/src/linux'):
            os.remove('/usr/src/linux')
        os.symlink('/usr/src/' + self._directory_name, 
            '/usr/src/linux')

    def _dry_set_symlink(self):
        """Dry run of _set_symlink.

        """
        if os.path.islink('/usr/src/linux'): 
            output.verbose("rm /usr/src/linux")
        output.verbose("ln -s /usr/src/%s /usr/src/linux", 
            self._directory_name)

    def _have_module_rebuild(self):
        """Determine if module-rebuild is installed or not.

        Using the new stuffs we've learned we can quickly determine
        if module-rebuild is installed on this system or not.

        """
        from gentoolkit.helpers import find_installed_packages
        installed = \
            find_installed_packages("sys-kernel/module-rebuild")
        if len(installed) < 1: return False
        return True

    def _get_install_image(self):
        """Get the image that will be created for this architecture.

        Return bzImage, vmlinux, etc depending on the arch of the 
        machine.

        From the kernel README:
          
        Although originally developed first for 32-bit x86-based PCs 
        (386 or higher), today Linux also runs on (at least) the Compaq
        Alpha AXP, Sun SPARC and UltraSPARC, Motorola 68000, PowerPC, 
        PowerPC64, ARM, Hitachi SuperH, Cell, IBM S/390, MIPS, 
        HP PA-RISC, Intel IA-64, DEC VAX, AMD x86-64, AXIS CRIS, 
        Xtensa, AVR32 and Renesas M32R architectures.

        We will support more of these as we get accurate reports of
        what the image produced by the default make command is.

        """
        arch = platform.machine()
        if self._debug: output.debug(__file__, {'arch':arch})

        if arch == "x86_64": return "bzImage"
        elif arch == "i686": return "bzImage"

        error_list = [
            "We do not know the output for your architecture. ",
            "Please, submit a bug report to",
            "http://bugzilla.alunduil.com with your architecture and",
            "the image that is created by default."
            ]
        raise KernelException(" ".join(error_list))

    def _get_kernel_names(self, kernel_name):
        """Gets the names for this kernel.

        Returns the qualified package name (emerge's name) as well as
        the directory for the sources.

        """
        emerge_expression_list = [
            '(?:sys-kernel/)?', # Just in case people want to pipe it
                                # in from portage.
            '(?:(?P<sources>[A-Za-z0-9+_][A-Za-z0-9+_-]*)-sources-)?',
            '(?P<version>[A-Za-z0-9+_][A-Za-z0-9+_.-]*)'
            ]
        emerge_expression = re.compile("".join(emerge_expression_list))
        emerge_match = emerge_expression.match(kernel_name)

        if self._debug:
            output.debug(__file__, {
                'emerge_match':emerge_match.group(0)
                })

        sources = "gentoo"

        emerge_name = "sys-kernel/"
        directory_name = ""
        if emerge_match:
            
            if emerge_match.group("sources"):
                sources = emerge_match.group("sources")
            emerge_name += sources
            emerge_name += "-sources-"
            emerge_name += emerge_match.group("version")
            if self._debug: 
                output.debug(__file__, {"emerge_name":emerge_name})
            
            # Get the directory name now.
            from gentoolkit.helpers import find_installed_packages
            installed = find_installed_packages(emerge_name)
            if self._debug:
                output.debug(__file__, {
                    "installed":installed
                    })
            if len(installed) < 1: 
                # @todo Make this more efficient.
                # Install the package requested.
                #from portage import merge
                #from gentoolkit import split_cpv
                #category, pkg_name, version, revision = \
                #    split_cpv(emerge_name)
                #merge(category, pkg_name+version+revision
                # @note The following is ugly!
                opts = ""
                if self._verbose: opts = "-v"
                command_list = ["emerge", opts, "="+emerge_name]
                # @todo Any better way to do this?
                if not self._dry_run and os.getuid != 0:
                    raise KernelException("Insufficient priveleges to continue!")
                if self._dry_run:
                    output.verbose(" ".join(command_list))
                    raise KernelException("Cannot continue dry run without sources")
                else:
                    os.system(" ".join(command_list))

            directories = self._get_kernel_directories()
            directories.reverse()
            from gentoolkit.helpers import FileOwner
            finder = FileOwner()
            for directory in directories:
                if self._debug:
                    output.debug(__file__, {
                        "directory":directory,
                        "finder(directory)":finder((directory,))[0][0],
                        "emerge_name":emerge_name
                        })
                if unicode(finder((directory,))[0][0]) == emerge_name.strip():
                    directory_name = directory
                    break
        else:
            directory_name = self._get_kernel_directories()[-1]
            from gentoolkit.helpers import FileOwner
            finder = FileOwner()
            emerge_name = finder((directory_name,))[0][0]

        if self._debug: 
            output.debug(__file__, {"directory_name":directory_name})
            output.debug(__file__, {"emerge_name":emerge_name})
        return (directory_name, emerge_name)

    def _get_kernel_directories(self):
        """Get the sorted and filtered list of kernel directories

        """
        if not os.access('/usr/src/', os.F_OK):
            raise KernelException("Could not access /usr/src/")
        src_list = os.listdir('/usr/src')
        src_list = filter(lambda x: re.match('linux-.+$', x), src_list)
        src_list.sort()
        return src_list
            
    def configure(self):
        """Configure the kernel sources.

        Using the parameters we have collected so far, let us configure
        the kernel sources we have prepared with the configurator that
        the user has selected from the strange choices we are given.

        """
        if not os.access('/usr/src/linux', os.X_OK):
            raise KernelException("Can't access the kernel source!")

        if self._dry_run:
            output.verbose("pushd /usr/src/linux")
        else:
            opwd = os.getcwd()
            os.chdir('/usr/src/linux')

        command_list = [
            "make", self._emerge_config["MAKEOPTS"], 
            self._configurator
            ]
        if self._dry_run:
            output.verbose(" ".join(command_list))
            output.verbose("popd")
        else:
            os.system(" ".join(command_list))
            os.chdir(opwd)

    def build(self):
        """Build the kernel.

        Build the kernel sources in /usr/src/linux, and if necessary 
        build the modules that portage has previously built for the 
        kernel.

        """
        if not os.access('/usr/src/linux', os.X_OK):
            raise KernelException("Can't access the kernel source!")

        if self._dry_run:
            output.verbose("pushd /usr/src/linux")
        else:
            opwd = os.getcwd()
            os.chdir('/usr/src/linux')

        command_list = [
            "make", self._emerge_config["MAKEOPTS"], "&& make",
            self._emerge_config["MAKEOPTS"], "modules_install"
            ]

        if self._dry_run:
            output.verbose(" ".join(command_list))
        else:
            os.system(" ".join(command_list))

        if self._rebuild_modules:
            if self._dry_run:
                output.verbose("module-rebuild -x rebuild")
            else:
                os.system('module-rebuild -X rebuild')
        if self._dry_run:
            output.verbose("popd")
        else:
            os.chdir(opwd)

    def install(self):
        """Install the kernel into /boot

        Get all appropriate kernel pieces into the boot area.

        """
        if not os.access('/usr/src/linux', os.X_OK):
            raise KernelException("Can't access the kernel source!")

        if self._dry_run:
            output.verbose("pushd /usr/src/linux")
        else:
            opwd = os.getcwd()
            os.chdir('/usr/src/linux')

        arch_dir = platform.machine()
        # The following should be necessary on x86 machines.
        # This needs to be double checked.
        if re.match('i\d86', arch_dir): arch_dir = "x86"

        if self._verbose: output.verbose("Architecture: %s", arch_dir)

        boot_mounted = False
        if not helpers.is_boot_mounted():
            if self._dry_run:
                output.verbose("mount /boot")
                output.error("--dry-run requires that you manually mount /boot")
            else:
                os.system('mount /boot')
            boot_mounted = True

        source_dir_list = [
            "arch/", arch_dir, "/boot/"
            ]
        if self._dry_run:
            output.verbose("cp %s%s /boot/%s%s", 
                "".join(source_dir_list), self._install_image, 
                self._install_image, self._suffix)
            output.verbose("cp .config /boot/config%s", self._suffix)
            output.verbose("cp System.map /boot/System.map%s", 
                self._suffix)
            output.verbose("cp System.map /System.map")
        else:
            shutil.copy("".join(source_dir_list) + self._install_image,
                '/boot/' + self._install_image + self._suffix)
            shutil.copy('.config', '/boot/config' + self._suffix)
            shutil.copy('System.map', '/boot/System.map' + \
                self._suffix)
            shutil.copy('System.map', '/System.map')

        if boot_mounted: 
            if self._dry_run:
                output.verbose("umount /boot")
            else:
                os.system('umount /boot')
        if self._dry_run:
            output.verbose("popd")
        else:
            os.chdir(opwd)

class KernelException(Exception):
    def __init__(self, message, *args):
        super(KernelException, self).__init__(args)
        self._message = message

    def get_message(self):
        return self._message

