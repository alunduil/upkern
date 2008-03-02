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

"""Contains necessary classes and functions to work with the kernel sources.

Will provide a Kernel class, and a generic kernel exception class.

"""

import os
import re

from helpers import is_boot_mounted

class KernelException(Exception):
    """Generic error class for a kernel problem.

    Specifies an error condition in the kernel module.

    """

    def __init__(self, message, *args):
        Exception.__init__(self, *args)
        self.message = message

    def print_message():
        print self.message

class Kernel(object):
    """A kernel handler object.

    Specifies an interface that allows the programmer to easily work with the
    kernel sources that the object gets bound to. This allows easy building,
    installing, and general manipulation of a kernel source directory.

    All references to how things should be called make an attempt to coincide
    with the documentation provided in the relevant kernel sources. This
    interface will attempt to stay in touch with the most recent kernel
    sources provided by the Gentoo Portage tree.

    See the following URL for a list of current kernels:
    http://packages.gentoo.org/package/sys-kernel/gentoo-sources

    kernel = Kernel(kernelName, sources, rebuildModules, buildMethod)

    """

    def __init__(self, configurator = "menuconfig", kernel_name = "",
        sources = "", rebuild_modules = True):
        """Returns a Kernel object with properly initialized data.

        Get the necessary information about the system to know how to perform
        basic kernel actions. We should be ready to configure, build, and
        install the kernel when this call completes.

        Post Conditions:
        The Kernel object is initialized, and the information has been
        populated.

        Returns:
        A Kernel object.

        """

        self.__configurator = configurator

        self.__sources = sources                # The sources as specified in
                                                # the gentoo portage tree.
                                                # (i.e. gentoo, vanilla, etc.)

        self.__kernel_name = kernel_name
        self.__download_name, self.__kernel_name = self.__get_kernel_names()

        self.__rebuild_modules = rebuild_modules

        self.__architecture = self.__determine_architecture()

        if not self.__are_sources_downloaded(): self.__download()

        self.__set_symlink()

        self.__copy_config()

        self.__make_opts = self.__get_make_opts()

    def __get_kernel_names(self):
        """Get the kernel name of the most up to date sources on the system.

        Returns the proper name of the sources we will be using for our build
        of the kernel.

        """
        if os.access('/usr/src/', os.F_OK):
            source_list = []
            source_list_full = []
            output = os.popen("emerge -s --quiet sources 2> /dev/null", "r")

            expression1 = re.compile(
                '^.+sys-kernel/(?P<source_type>\S+)-sources\s+$')
            expression2= re.compile(
                '^.+sys-kernel/(?P<source_type>\S+)-sources.+$')

            for line in output.readlines():
                match1 = expression1.match(line)
                match2 = expression2.match(line)
                if match1:
                    source_list.append(match1.group("source_type"))
                    source_list_full.append(match1.group("source_type"))
                elif match2:
                    source_list_full.append(match2.group("source_type"))

            tmp_expression = [
                '^(?P<version>((\d+\.){2}\d+))',
                '(-(?P<source_type>.+?))?(?P<release>-r\d+)?$'
                ]
            expression3 = re.compile(''.join(tmp_expression))

            tmp_expression = [
                '^((?P<source_type>.+?)-)?(sources-)?',
                '(?P<version>((\d+\.){2}\d+))(?P<release>-r\d+)?$'
                ]
            expression4 = re.compile(''.join(tmp_expression))

            match3 = expression3.match(self.__kernel_name) or \
                expression4.match(self.__kernel_name)
            if match3 and match3.group("source_type"):
                for source_type in source_list:
                    if match3.group("source_type") == source_type:
                        break
                else:
                    for source_type in source_list_full:
                        if match3.group("source_type") == source_type:
                            raise KernelException("Sources are masked!",
                                match3.group("source_type"))
                    else:
                        raise KernelException(
                            "Sources do not exist in portage!",
                            match.group("sourceType"))
            elif not match3:
                raise KernelException("Kernel did not match any in portage!")

            return ( \
                (match3.group("source_type") or self.__sources or "gentoo") + \
                "-sources-" + match3.group("version") + \
                (match3.group("release") or ""), "linux-" + \
                match3.group("version") + "-" + \
                (match3.group("source_type") or self.__sources or "gentoo") \
                + (match3.group("release") or ""))

    name = property(__get_kernel_names, doc='Name of the kernel.')

    def __determine_architecture(self):
        """Determine the architecture of the running machine.

        Return the architecture string of the machine we are currently running
        on.

        """

        return os.popen('uname -m', 'r').readline().strip()

    def __are_sources_downloaded(self):
        """Determine if the kernel sources the user wants are downloaded.

        If the kernel sources are downloaded return true, otherwise return
        false.

        """

        expression = re.compile('^(\..+)|(snort_dynamicsrc)$')

        directories = os.listdir('/usr/src/')
        directories.sort(reverse=True)

        for directory in directories:
            if not expression.match(directory) and self.__kernel_name == directory:
                return True
        return False

    def __download(self):
        """Download the kernel sources we have associated with this object.

        Download the sources for the kernel we are interesting in.

        """

        output = os.popen('emerge -p =' + self.__download_name, 'r')

        expression1 = re.compile('^emerge: there are no ebuilds to satisfy.+$')
        expression2 = re.compile('^.+masked by:\s(?P<keyword>.+?)\s.+$')

        for line in output.readlines():
            match = expression2.match(line)
            if expression1.match(line):
                raise KernelException("Kernel sources not found!", self.__downloadName)
            elif match:
                raise KernelException("Kernel sources are masked by portage!",
                    self.__downloadName, match.group("keyword"))
        else:
            os.system('emerge -v =' + self.__download_name)

    def __set_symlink(self):
        """Set the kernel symlink (/usr/src/linux).

        Properly determines and sets the linux kernel symlink.

        """

        if os.path.islink('/usr/src/linux'):
            os.remove('/usr/src/linux')
        os.symlink('/usr/src/' + self.__kernel_name, '/usr/src/linux')

    def __copy_config(self):
        """Copy an old kernel configuration file from /boot.

        Copies a previous kernel configuration file that upkern has created
        from the boot area, and uses that for the creation of this kernel.

        """

        if is_boot_mounted():
            expression = re.compile('^/boot/config-.+$')

            directories = os.listdir('/boot')
            directories.sort(reverse=True)

            for directory in directories:
                match = expression.match(directory)

                if match:
                    shutil.copy(match.group(), '/usr/src/linux/.config')
                    break
            else:
                raise KernelException(
                    "Old configuration not found! Using default!");
        else:
            os.system('mount /boot')
            self.copy_config()
            os.system('umount /boot')

    def configure(self, verbosity = 0):
        """Configure the kernel sources.

        Using the parameters we have collected so far, let us configure the
        kernel sources we have prepared with the configurator that the user
        has selected from the strange choices we are given.

        """

        os.chdir('/usr/src/linux')

        expression = re.compile('^/usr/src/linux.+$')
        if not expression.match(os.getcwd()):
            raise KernelException("Could not cd into /usr/src/linux!")

        if len(self.__configurator) <= 0:
            self.__configurator = "menuconfig"

        tmp_expression = [
            '^(',
            'menuconfig|',
            'xconfig|',
            'gconfig|',
            'oldconfig|',
            'silentoldconfig|',
            'defconfig|',
            'allyesconfig|',
            'allmodconfig|',
            'allnoconfig|',
            'randconfig',
            ')$'
            ]
        expression1 = re.compile(''.join(tmp_expression))
        expression2 = re.compile('^(menuconfig|oldconfig|silentoldconfig)$')

        match = expression2.match(self.__configurator)

        if expression1.match(self.__configurator):
            if verbosity <= 0:
                if match:
                    os.system('make -s ' + self.__make_opts + ' ' + \
                        self.__configurator + ' 2>/dev/null')
                else:
                    os.system('make ' + self.__make_opts + ' ' + \
                        self.__configurator + '>/dev/null 2>/dev/null')
            elif verbosity == 1 or verbosity == 2:
                if match:
                    os.system('make -s ' + self.__make_opts + ' ' + \
                        self.__configurator)
                else:
                    os.system('make ' + self.__make_opts + ' ' + \
                        self.__configurator + '>/dev/null')
            else:
                os.system('make ' + self.__make_opts + ' ' + \
                    self.__configurator)
        else:
            raise KernelException("Configurator not supported!", \
                self.__configurator)

    def __get_make_opts(self):
        """Get the MAKEOPTS defined in the /etc/make.conf file.

        Use the MAKEOPTS defined in the /etc/make.conf file so we can perform
        as much of the build as possible in parallel. Potentially, speeding up
        the process by a significant amount.

        """

        expression = re.compile('^MAKEOPTS="(?P<make_opts>.+?)"$')

        output = os.popen('fgrep MAKEOPTS /etc/make.conf', 'r').readline()

        if (len(output) > 0):
            match = expression.match(output)
            return match.group("make_opts")
        return ""

    def build(self, verbosity = 0):
        """Build the kernel.

        Build the kernel sources in /usr/src/linux, and if necessary build
        the modules that portage has previously built for the kernel.

        """

        os.chdir('/usr/src/linux')

        expression = re.compile('^/usr/src/linux.+$')
        if not expression.match(os.getcwd()):
            raise KernelException("Could not cd into /usr/src/linux!")

        expression = re.compile('^.+(?P<version>\d+\.\d+)\..+$')

        version = expression.match(self.__kernel_name).group("version")

        if verbosity > 2:
            output = ''
        elif verbosity == 1 or verbosity == 2:
            output = '>/dev/null'
        elif verbosity <= 0:
            output = '>/dev/null 2>/dev/null'

        if version == "2.4":
            if self.__architecture == "sparc32":
                os.system('make ' + self.__make_opts + ' dep' + output + \
                    '&& make ' + self.__make_opts + \
                    ' clean vmlinux modules modules_install' + output)
            elif self.__architecture == "sparc64":
                os.system('make ' + self.__make_opts + ' dep' + output + \
                    '&& make ' + self.__make_opts + \
                    ' clean vmlinux image modules modules_install' + output)
            else:
                os.system('make ' + self.__make_opts + ' dep' + output + \
                    '&& make ' + self.__make_opts + \
                    ' bzImage modules modules_install' + output)
        elif version == "2.6":
            if self.__architecture == "sparc64":
                os.system('make ' + self.__make_opts + ' ' + output + \
                    '&& make ' + self.__make_opts + ' image modules_install' \
                    + output)
            else:
                os.system('make ' + self.__make_opts + ' ' + output + \
                    '&& make ' + self.__make_opts + ' modules_install' \
                    + output)
        if self.__rebuild_modules:
            os.system('module-rebuild -X rebuild' + output)
