#!/usr/bin/env python -t3
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

import portage.config
import re

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
        rebuild_modules = True, debug = False, verbose = False):
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
        self._configurator = configurator

        self._qualified_package_name = \
            self._get_package_name(kernel_name)

        self._kernel_suffix, self._kernel_version = \
            self._split_kernel_name(self._kernel_directory)
        self._architecture = self._determine_architecture()

        self._install_image = self._get_install_image()

        self._rebuild_modules = False
        if rebuild_modules and self._have_rebuild_modules():
            self._rebuild_modules = rebuild_modules

        if not self._have_sources(): self._install_sources()

        self._set_symlink()
        self._copy_config()

        self._emerge_config = portage.config()

    def _get_package_name(self, kernel_name):
        """Gets the names for this kernel.

        Returns the qualified package name (emerge's name).

        """
        emerge_expression_list = [
            '(?:sys-kernel/)?', # Just in case people want to pipe it
                                # in from portage.
            '(?:(?P<sources>[A-Za-z0-9+_][A-Za-z0-9+_-]*?)-sources-)?',
            '(?P<version>[A-Za-z0-9+_][A-Za-z0-9+_.-]*)'
            ]
        emerge_expression = re.compile("".join(emerge_expression_list)
        emerge_match = emerge_expression.match(kernel_name)

        sources = "gentoo"

        qualified_package_name = "sys-kernel/"
        if emerge_match:
            if emerge_match.group("sources"):
                sources = emerge_match.group("sources")
            qualified_package_name += sources
            qualified_package_name += "-sources-"
            qualified_package_name += emerge_match.group("version")
            if self._debug:
                print >> sys.stderr, 
                    "%s:%s: DEBUG: qualified_package_name -> %s" % \
                    __file__, __line__, qualified_package_name
            # Get the directory name now.


        else:
            # Look at the installed sources for one to use.
            if not os.access('/usr/src/', os.F_OK):
                raise KernelExcpetion("Could not access /usr/src/")
            src_list = os.listdir('/usr/src/')
            src_list = filter(lambda x: re.match('linux-.+$', x), src_list)
            src_list.sort()
            directory_name = src_list[-1]
            equery

            
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
                '^(?P<version>((\d+\.)+\d+))',
                '(-(?P<source_type>.+?))?(?P<release>-r\d+)?$'
                ]
            expression3 = re.compile(''.join(tmp_expression))

            tmp_expression = [
                '^((?P<source_type>.+?)-)?(sources-)?',
                '(?P<version>((\d+\.)+\d+))(?P<release>-r\d+)?$'
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

            ret1 = (match3.group("source_type") or self.__sources or "gentoo") + \
                "-sources-" + match3.group("version") + \
                (match3.group("release") or "")
            ret2 = "linux-" + match3.group("version")
            if match3.group("source_type") != "vanilla":
                ret2 += "-" + \
                    (match3.group("source_type") or self.__sources or "gentoo") \
                    + (match3.group("release") or "")

            return ret1, ret2

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
                raise KernelException("Kernel sources not found!", self.__download_name)
            elif match:
                raise KernelException("Kernel sources are masked by portage!",
                    self.__download_name, match.group("keyword"))
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
            expression = re.compile('^config-.+$')

            directories = os.listdir('/boot')
            directories.sort(reverse=True)

            for directory in directories:
                match = expression.match(directory)

                if match:
                    shutil.copy('/boot/' + match.group(),
                        '/usr/src/linux/.config')
                    break
            else:
                warn("Old configuration not found! Using default!");
        else:
            os.system('mount /boot')
            self.__copy_config()
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

        if self.__boot_splash:
            error_list = [
                'Bootsplash requires certain kernel configuration options',
                'to be set:\n',
                '\tSupport for frame buffer devices\n',
                '\tVESA VGA graphics support\n',
                '\tVESA driver type (vesafb-tng)\n',
                '\tVideo mode selection support\n',
                '\tFramebuffer Console support\n',
                '\tSupport for the Framebuffer Console Decorations\n',
                '\n',
                'Make sure you didn\'t select tileblitting support.\n',
                'If you are using an AMD64 processor, you should select',
                'vesafb rather than vesafb-tng. Also note for x86 and AMD64',
                'processors, the in-kernel nvidia framebuffer driver',
                'conflicts with the binary driver provided by nVidia. If you',
                'will be compiling your kernel for these CPUs, you must',
                'completely remove support for the in-kernel driver as shown',
                'above. See http://www.gentoo.org/doc/en/nvidia-guide.xml',
                'for Details.\n',
                '\n',
                'Be sure to set your personal resolution@freq',
                '(e.g. 1024x768@72) the default is 640x480@60. Now you\'ll',
                'probably want to have both the initial ramdisk (initrd',
                'which stores the image) to along with it\'s filesystem',
                'loaded at boot.\n',
                '\n',
                '\tInitial RAM filesystem and RAM disk (initramfs/initrd) support\n'
                ]
            warn(' '.join(error_list))

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

    def __get_image_name(self):
        """Get the image name for the compiled kernel.

        Determine if the kernel will be a bzImage, image, vmlinux, etc.

        """

        expression = re.compile('^i\d86$')

        if expression.match(self.__architecture) or \
            self.__architecture == "x86_64":
            return "bzImage"
        elif self.__architecture == "sparc64":
            return "image"
        elif self.__architecture == "sparc32":
            if self.__kernel_version == "2.4":
                return "vmlinux"
            elif self.__kernel_version == "2.6":
                return "image"

        raise KernelException( \
            "Could not determine the image for your architecture!", \
            self.__architecture)

    def build(self, verbosity = 0):
        """Build the kernel.

        Build the kernel sources in /usr/src/linux, and if necessary build
        the modules that portage has previously built for the kernel.

        """

        os.chdir('/usr/src/linux')

        expression = re.compile('^/usr/src/linux.+$')
        if not expression.match(os.getcwd()):
            raise KernelException("Could not cd into /usr/src/linux!")

        if verbosity > 2:
            output = ''
        elif verbosity == 1 or verbosity == 2:
            output = '>/dev/null'
        elif verbosity <= 0:
            output = '>/dev/null 2>/dev/null'

        if self.__kernel_version == "2.4":
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
        elif self.__kernel_version == "2.6":
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

    def install(self, verbosity = 0):
        """Install the kernel into /boot

        Get the appropriate kernel pieces into the boot area.

        """
        os.chdir('/usr/src/linux')

        expression = re.compile('^/usr/src/linux.+$')
        if not expression.match(os.getcwd()):
            raise KernelException("Could not cd into /usr/src/linux!")

        expression = re.compile('^i\d86$')

        destination = '/boot/' + self.__kernel_image + self.__kernel_suffix

        if is_boot_mounted():
            if expression.match(self.__architecture):
                shutil.copy('arch/i386/boot/' + self.__kernel_image, \
                    destination)
            elif self.__architecture == "sparc64" or \
                self.__architecture == "x86_64":
                shutil.copy('arch/' + self.__architecture + '/boot/' + \
                    self.__kernel_image, destination)
            elif self.__architecture == "sparc32":
                if self.__kernel_version == "2.4":
                    shutil.copy(self.__kernel_image, destination)
                elif self.__kernel_version == "2.6":
                    shutil.copy('arch/sparc/boot/' + self.__kernel_image, \
                        destination)

            shutil.copy('.config', '/boot/config' + self.__kernel_suffix)
            shutil.copy('System.map', '/boot/System.map' + self.__kernel_suffix)
            shutil.copy('System.map', '/System.map')
        else:
            os.system('mount /boot')
            self.install()
            os.system('umount /boot')

    def __install_rebuild_modules(self):
        expression = re.compile('^\[ebuild\s+(R|U)\s+\].+$')

        output = os.popen('emerge -p module-rebuild 2>/dev/null | tail -n1', 'r')

        if not expression.match(output.readline()):
            os.system('emerge -v module-rebuild')

    def __install_boot_splash(self):
        expression = re.compile('^\[ebuild\s+(?P<status>N|R|U)\s+\]\s+(?P<package>.*?(splashutils|splash-themes-gentoo|splash-themes-livecd).*?)\s+.*?$')

        output = os.popen('USE=fbcondecor emerge -p splashutils splash-themes-gentoo splash-themes-livecd')

        for line in output:
            match = expression.match(line)
            if match:
                if match.group("status") == "N":
                    os.system('USE=fbcondecor emerge -v ' + match.group("package"))