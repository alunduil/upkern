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

class Sources(object):
    """A kernel source model.

    Specifies an interface that allows the programmer to easily work with the 
    kernel sources that the object gets bound to.  This allows easy building, 
    installing and controlled manipulation of a kernel source directory.

    All references to how things should be called makes an attempt to coincide
    with the documentation provided in the relevant kernel sources.  If
    mismatches are discovered bugs should be reported to
    http://bugs.alunduil.com.  The reference sources will be those provided by
    the Gentoo Portage tree.

    See the following URL for a list of current kernel sources:
    http://packages.gentoo.org/packages/sys-kernel/gentoo-sources

    """

    def __init__(self, name = "", debug = False, verbose = False,
            quiet = False, dry_run = False): 
        """Returns a kernel sources object.

        Get the appropriate information about the system to know how to perform
        basic kernel actions.  Once the initial data discovery is complete
        (within this method), the normal sequence to build a kernel is the
        following:

        kernel.Source.prepare(configuration = <config file path>)
        kernel.Source.configure(configurator = <configurator>)

        """

        self.arguments = {
                "debug": debug,
                "verbose": verbose,
                "quiet": quiet,
                "dry_run": dry_run,
                }

        if not self.arguments["quiet"]:
            wait_notice_list = [
                    "Getting information about the kernel sources ... this ",
                    "could take a while ... please wait ...",
                    ]
            print("".join(warn_notice_list))

    @property
    def directory_name(self):
        pass # self._get_kernel_names(kernel_name)

    @property
    def package_name(self):
        pass # self._get_kernel_names(kernel_name)

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
    def suffix(self):
        pass # "-" + self._directory_name.partition('-')[2]

    def prepare(self, configuration = ""):
        self._set_symlink()
        self._copy_config(configuration)

    def configure(self, configurator = ""):
        pass

    def build(self):
        portage_config = portage.config()

    def rebuild_modules(self):
        if not hasattr(self.rebuild_modules, "has_rebuild_modules"):
            self.rebuild_modules.has_rebuild_modules = \
                    not len(GentoolkitQuery("sys-kernel/module-rebuild").find_installed())

        if not self.rebuild_modules.has_rebuild_modules:
            return

        if self.arguments["verbose"]:
            helpers.verbose("Rebuilding Modules: True")

    @mountedboot
    def _copy_config(self, configuration = ""):
        """Copy the configuration file into /usr/src/linux/.config.
        
        This operation can be assumed to be atomic.  If a failure occurs all
        actions taken up to that point shall be reverted and an appropriate 
        exception raised.
        
        """

        # If no configuration file is passed; find the highest versioned one
        # in /boot.
        if not len(configuration):
            config_list = [ 
                    f for f in os.listdir('/boot') \
                            if re.match('config-.+', f) 
                    ]

            keys = map(self._create_kernel_key, config_list)
            config_dict = dict(zip(keys, config_list))

            config_list = map(lambda x: config_dict[x], 
                    sorted(config_dict.keys()))

            if len(config_list):
                configuration = config_list[-1]

        # If we didn't find a configuration file there is nothing further to
        # do and we can return.
        if not len(configuration):
            return

        if self.arguments["verbose"]:
            helpers.verbose("Using Configuration File: %s", configuration)

        # Perform the necessary actions (outlined in dry_run performed 
        # otherwise).  Keeping in mind that any action on the system itself
        # must be undone if an error occurs.
        if self.arguments["dry_run"]:
            dry_list = [
                    "cp /usr/src/linux/.config{,.bak}",
                    "cp /boot/%s /usr/src/linux/.config",
                    ]
            helpers.colorize("GREEN", 
                    "\n".join(dry_list).format(configuration))
        else:
            try:
                shutil.copy('/usr/src/linux/.config', 
                        '/usr/src/linux/.config.bak')
                shutil.copy('/boot/%s'.format(configuration), 
                        '/usr/src/linux/.config')
            except Exception e:
                if os.access("/usr/src/linux/.config.bak", os.W_OK):
                    os.remove("/usr/src/linux/.config")
                    os.rename("/usr/src/linux/.config.bak", 
                            "/usr/src/linux/.config")
                raise e

    def _set_symlink(self):
        """Sets the symlink to the new kernel directory.
        
        This operation can be assumed to be atomic.  If a failure occurs all
        actions taken up to that point shall be reverted and an appropriate
        exception raised.
        
        """

        original = None

        if os.path.islink('/usr/src/linux'):
            original = os.readlink("/usr/src/linux")

            if self.arguments["dry_run"]:
                helpers.colorize("GREEN", "rm /usr/src/linux"))
            else:
                try:
                    os.remove('/usr/src/linux')
                except Exception e:
                    os.symlink(original, "/usr/src/linux")
                    raise e

        if self.arguments["dry_run"]:
            dry_list = [
                    "ln -s /usr/src/%s /usr/src/linux",
                    ]
            helpers.colorize("GREEN", 
                    "\n".join(dry_list).format(self.directory_name))
        else:
            try:
                os.symlink('/usr/src/%s'.format(self.directory_name),
                        '/usr/src/linux')
            except Exception e:
                os.remove("/usr/src/linux")
                os.symlink(original, "/usr/src/linux")
                raise e

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

        if self._debug and emerge_match:
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
            from gentoolkit.query import Query
            installed = Query(emerge_name).find_installed()
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
                opts = []
                if self._verbose: opts.append("-v")
                if self._quiet: opts.append("-q")
                command_list = ["emerge", " ".join(opts), "="+emerge_name]
                # @todo Any better way to do this?
                if not self._dry_run and os.getuid() != 0:
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

        keys = map(self._create_kernel_key, src_list)
        kernel_dict = dict(zip(keys, src_list))

        if self._debug: output.debug(__file__, {"keys": keys, "src_list": src_list, "kernel_dict": kernel_dict})

        result_list = map(lambda x: kernel_dict[x], sorted(kernel_dict.keys()))
        if self._debug: output.debug(__file__, {"result_list": result_list})
        
        return result_list

    def _create_kernel_key(self, kernel_string):
        """Convert a kernel string into majorminorpatch.revision notation
        """
        if self._debug: output.debug(__file__, {"kernel_string": kernel_string})
        
        regex = '.*?(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?-[^-]*(?:-r(?P<revision>\d+))?'
        if self._debug: output.debug(__file__, {"regex": regex})
        m = re.match(regex, kernel_string)
        
        revision = major = minor = patch = 0
        if m:
            if m.group("revision"): 
                revision = int(m.group("revision"))
            if m.group("major"):
                major = int(m.group("major"))
            if m.group("minor"):
                minor = int(m.group("minor"))
            if m.group("patch"):
                patch = int(m.group("patch"))

        if self._debug: output.debug(__file__, {"revision": revision})
       
        key = "%03d%03d%03d.%03d" % (major, minor, patch, revision)
        if self._debug: output.debug(__file__, {"key": key})
        
        return key
            
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

        makeopts = self._emerge_config["MAKEOPTS"]
        if self._quiet: makeopts += " -s"

        command_list = [
            "make", makeopts, "&& make", makeopts, "modules_install"
            ]

        if self._dry_run:
            output.verbose(" ".join(command_list))
        else:
            os.system(" ".join(command_list))

        if self._rebuild_modules:
            if self._dry_run:
                output.verbose("module-rebuild -X rebuild")
            else:
                os.system('module-rebuild -X rebuild')
        if self._dry_run:
            output.verbose("popd")
        else:
            os.chdir(opwd)

    def _get_modules_directory(self):
        """Get the modules directory of the kernel.

        """
        return "/lib/modules/" + self._directory_name.split("/")[-1]

    def remove(self):
        """Remove the kernel from the system.

        Remove the kernel by removing the following things:
         * /usr/src/<sources>
         * /lib/modules/<sources>
         * /boot/<stuff>
         * GRUB entry

        """
        
        # Determine if we are running the kernel we just removed:
        running = Kernel(self._configurator, 
            self._get_running_kernel_cpv(), self._rebuild_modules,
            self._configuration, False, False, True, True)

        if self.get_name() == running.get_name():
            output.status("Will not remove the running kernel.  Please install a different kernel and boot into it before proceeding.")
            raise KernelException("Cowardly refusing to remove the currently working kernel!")

        # @todo Make this more efficient.
        # Install the package requested.
        #from portage import merge
        #from gentoolkit import split_cpv
        #category, pkg_name, version, revision = \
        #    split_cpv(emerge_name)
        #merge(category, pkg_name+version+revision
        # @note The following is ugly!
        opts = ["-C"]
        if self._verbose: opts.append("-v")
        command_list = ["emerge", " ".join(opts), "="+self._emerge_name]

        # @todo Any better way to do this?
        if not self._dry_run and os.getuid() != 0:
            raise KernelException("Insufficient priveleges to continue!")

        if self._dry_run:
            output.verbose(" ".join(command_list))
            output.verbose("rm -rf /usr/src/%s" % self._directory_name)
            output.verbose("rm -rf %s" % self._get_modules_directory())
        else:
            os.system(" ".join(command_list))
            helpers.recursive_remove("/usr/src/" + self._directory_name)
            helpers.recursive_remove(self._get_modules_directory())
        
        boot_mounted = False
        if not helpers.is_boot_mounted():
            if self._dry_run:
                output.verbose("mount /boot")
                output.error("--dry-run requires that you manually mount /boot")
            else:
                os.system('mount /boot')
            boot_mounted = True

        if self._dry_run:
            output.verbose("rm /boot/%s%s", self._install_image, 
                self._suffix)
            output.verbose("rm /boot/config%s", self._suffix)
            output.verbose("rm /boot/System.map%s", self._suffix)
        else:
            os.remove('/boot/' + self._install_image + self._suffix)
            os.remove('/boot/config' + self._suffix)
            os.remove('/boot/System.map' + self._suffix)

        if boot_mounted: 
            if self._dry_run:
                output.verbose("umount /boot")
            else:
                os.system('umount /boot')

        # re-symlink the kernel so we leave the system consistent ...
        if self._dry_run:
            if os.path.islink('/usr/src/linux'): 
                output.verbose("rm /usr/src/linux")
            output.verbose("ln -s /usr/src/%s /usr/src/linux", 
                running.get_name())
        else:
            if os.path.islink('/usr/src/linux'):
                os.remove('/usr/src/linux')
            os.symlink('/usr/src/' + running.get_name(), 
                '/usr/src/linux')

        # Remove from bootloader handled in bootloader?
        # For now let's say yes.

    def _get_running_kernel_cpv(self):
        """Get the current running kernel's CPV for portage searches.

        """
        import platform
        system, node, release, version, machine, processor = platform.uname()
        if self._debug: output.debug(__file__, {'release':release})
        tmp = release.split('-')
        kernel_cpv = [tmp[0]]
        if re.search("^rc", tmp[1]):
            kernel_cpv[0] = "vanilla-sources-" + kernel_cpv[0]
            kernel_cpv.append(tmp[1])
            join_char = "_"
        else:
            kernel_cpv.extend([tmp[1], tmp[2]])
            join_char = "-"

        return join_char.join(kernel_cpv)
        
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

