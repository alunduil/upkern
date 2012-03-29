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
                "name": name,
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
        """Get the sources directory."""
        if not hasattr(self, "_directory_name"):
            finder = FileOwner()

            for directory in self.source_directories:
                if unicode(finder((directory, ))[0][0]) == self.package_name.lstrip("="):
                    self._directory_name = directory
                    break

        return self._directory_name

    @property
    def package_name(self):
        """Get the package name of the kernel we're dealing with."""
        if not hasattr(self, "_package_name"):
            package_expression_list = [
                    r"(?:sys-kernel/)?", # For piping from portage ...
                    r"(?:(?P<sources>[+\w][+-\w]*)-sources-)?",
                    r"(?P<version>[+\w][+-.\w]*)",
                    ]
            package_expression = re.compile("".join(emerge_expression_list))
            package_match = package_expression.match(self.arguments["name"])

            sources = "gentoo"

            self._package_name = "=sys-kernel/"

            if package_match:
                if package_match.group("sources"):
                    sources = package_match.group("sources")
                self._package_name += sources
                self._package_name += "-sources-"
                self._package_name += package_match.group("version")
            else:
                finder = FileOwner()
                self._package_name = unicode(finder((self.source_directories[0], ))[0][0])

        return self._package_name

    @property
    def source_directories(self):
        """Get the list of sorted source directories on the system."""

        if not hasattr(self, "_source_directories"):
            self._directories = [ d for d in os.listdir('/usr/src') if re.match(r"linux-.+$", d) ]

            keys = [ self._keyify(d) for d in directories ]
            dict_ = dict(zip(keys, directories))

            self._directories = [ dict_[d] for d in sorted(dict_.keys(), reverse = True) ]

        return self._directories

    @property
    def suffix(self):
        pass # "-" + self._directory_name.partition('-')[2]

    def prepare(self, configuration = ""):
        self._install_sources()
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

    def _install_sources(self):
        """Installs the requested kernel sources using portage.

        This operation can be assumed to be atomic.  If a failure occurs all
        actions taken up to that point shall be reverted and an appropriate
        exception raised.

        """

        if not len(GentoolkitQuery(self.package_name).find_installed()):
            opts = [
                    "-n",
                    "-1",
                    ]

            if self.arguments["verbose"]:
                opts.append("-v")

            if self.arguments["quiet"]:
                opts.append("-q")

            command = "emerge %s %s".format(" ".join(opts),
                    self.package_name)
            
            if self.arguments["dry_run"]:
                helpers.colorize("GREEN", command)
            else:
                if helpers.sufficient_privileges():
                    # TODO Can this fail in a way we need to revert?
                    status = subprocess.call(command, shell = True)
                    if status != 0:
                        pass # Raise an appropriate exception.

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
            config_list = [ f for f in os.listdir('/boot') if re.match('config-.+', f) ]

            keys = [ self._keyify(c) for c in config_list ]
            dict_ = dict(zip(keys, config_list))

            config_files = [ dict_[k] for k in sorted(dict_.keys()) ] 

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

    def _keyify(self, kernel_string):
        """Convert a kernel string into majorminorpatch.revision notation."""
        
        regex = '.*?(?P<major>\d+)\.(?P<minor>\d+)(?:\.(?P<patch>\d+))?-[^-]*(?:-r(?P<revision>\d+))?'
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

        key = "%03d%03d%03d.%03d".format(major, minor, patch, revision)
        
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

