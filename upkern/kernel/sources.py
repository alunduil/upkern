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
    def portage_config(self):
        if not hasattr(self, "_portage_config"):
            self._portage_config = portage.config()
        return self._portage_config

    def prepare(self, configuration = ""):
        self._install_sources()
        self._set_symlink()
        self._copy_config(configuration)

    def configure(self, configurator = ""):
        """Configure the kernel sources."""

        original_directory = os.getcwd()

        command = "make %s %s".format(self.portage_config["MAKEOPTS"],
                configurator)

        if self.arguments["dry_run"]:
            dry_list = [
                    "pushd /usr/src/linux",
                    command,
                    "popd",
                    ]
            helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            os.chdir('/usr/src/linux')
            status = subprocess.call(command, shell = True)
            os.chdir(original_directory)
        
    def build(self):
        """Build the kernel."""

        original_directory = os.getcwd()

        make_options = self.portage_config["MAKEOPTS"]
        if self.arguments["quiet"]:
            make_options += " -s"

        command = "make %s && make %s modules_install".format(make_options, make_options)

        if self.arguments["dry_run"]:
            dry_list = [
                    "pushd /usr/src/linux",
                    command,
                    "popd",
                    ]
            helpers.colorize("GREEN", "\n".join(dry_list))
        else:
            os.chdir("/usr/src/linux")
            status = subprocess.call(command, shell = True)
            os.chdir(original_directory)

        return Binary(self.directory_name)

    def rebuild_modules(self):
        if not hasattr(self.rebuild_modules, "has_rebuild_modules"):
            self.rebuild_modules.has_rebuild_modules = \
                    not len(GentoolkitQuery("sys-kernel/module-rebuild").find_installed())

        if not self.rebuild_modules.has_rebuild_modules:
            return

        if self.arguments["verbose"]:
            helpers.verbose("Rebuilding Modules: True")

        if self.arguments["dry_run"]:
            helpers.colorize("GREEN", "module-rebuild -X rebuild")
        else:
            status = subprocess.call("module-rebuild -X rebuild")

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
                helpers.colorize("GREEN", "rm /usr/src/linux")
            else:
                try:
                    os.remove('/usr/src/linux')
                except Exception as error:
                    os.symlink(original, "/usr/src/linux")
                    raise error

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
            
    def _get_modules_directory(self):
        """Get the modules directory of the kernel.

        """
        return "/lib/modules/" + self._directory_name.split("/")[-1]

