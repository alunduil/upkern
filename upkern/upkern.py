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

import time
import sys
import optparse
import textwrap
import os

from kernel import Kernel, KernelException
from bootloader import BootLoader, BootLoaderException, GrubException

class Upkern:
    def __init__(self, argv):
        self._debug = False
        self._verbose = False
        self._kernel_name = ""
        self._configurator = ""
        self._rebuild_modules = False
        self._time_build = False
        self._quiet = False
        self._kernel_options = ""
        self._editor = ""

        usage = "usage: %prog [options] kernel"
        parser = optparse.OptionParser(usage=usage)
        variables, arguments = self._parseOptions(argv, parser)

        self._quiet = variables.quiet
        self._debug = variables.debug
        # If we have debugging turned on we should also have verbose.
        if self._debug: self._verbose = True
        else: self._verbose = variables.verbose
        # If we have verbose we shouldn't be quiet.
        if self._verbose: self._quiet = False

        if len(arguments) > 0: self._kernel_name = arguments[0]

        self._configurator = variables.configurator
        self._rebuild_modules = variables.rebuild_modules
        self._time_build = variables.time_build
        self._kernel_options = variables.kernel_options
        self._configuration = variables.configuration
        #self._editor = variables.editor # @todo Make this sane.
        self._dry_run = variables.dry_run
        self._remove = variables.remove

    def Run(self):
        try:
            # Handle the kernel parts.
            kernel = Kernel(self._configurator,
                self._kernel_name, self._rebuild_modules, 
                self._configuration, self._debug, self._verbose, 
                self._quiet, self._dry_run)

            if self._remove:
                kernel.remove()
            else:
                kernel.configure()
                if self._time_build: start_time = time.time()
                kernel.build()
                if self._time_build: stop_time = time.time()
                kernel.install()
        except KernelException, e:
            raise UpkernException(e.get_message())

        try:
            # Handle the boot loader stuffs.
            boot_loader = BootLoader(kernel, self._kernel_options, 
                self._debug, self._verbose, self._quiet, self._dry_run)
            boot_loader.create_configuration()
            boot_loader.install_configuration()
        except BootLoaderException, e:
            raise UpkernException(e.get_message())
        except GrubException, e:
            raise UpkernException(e.get_message())

        if self._editor:
            command_list = [
                self._editor, boot_loader.get_config_url()
                ]
            os.system(" ".join(command_list))

        final_output_message_list = [
            "The kernel, ", kernel.get_name(), 
            ", has been successfully installed.",
            ]
        if self._time_build:
            hours = int((stop_time - start_time)/3600)
            minutes = int(((stop_time - start_time) % 3600)/60)
            seconds = int((stop_time - start_time) % 60)
            final_output_message_list.append( \
                "  The time to build the kernel was: " + str(hours) + \
                ":" + str(minutes) + ":" + str(seconds) + ".")
        final_output_message_list[len(final_output_message_list):] = [
            "  Please, check that all config files are in the ",
            "appropriate place and that there are no errors in the ",
            "configuration of the boot process.  It would be ",
            "unfortunate if you were not able to boot the kernel we ",
            "just prepared."
            ]
        for string in textwrap.wrap(''.join(final_output_message_list)):
            print string

    def _parseOptions(self, argv, parser):
        configurators = ["config", "menuconfig", "xconfig", "gconfig",
            "oldconfig", "silentoldconfig", "defconfig",
            "${PLATFORM}_defconfig", "allyesconfig", "allmodconfig",
            "allnoconfig", "randconfig"
            ]
        configurator_help_list = [
            "Specifies which configurator should be used to configure ",
            "the kernel sources.  The configurator can be one of the ",
            "following: " + ", ".join(configurators) + ".  All the ",
            "configurators are documented in the kernel source files."
            ]
        parser.add_option('--configurator', '-c', type='choice',
            choices=configurators, default='menuconfig',
            help=''.join(configurator_help_list))

        options_help_list = [
            "This string is literally tacked onto the kernel options ",
            "in your boot loader's configuration file.  This is the ",
            "place you would want to stick a framebuffer line, or any ",
            "other options you want your kernel to have."
            ]
        parser.add_option('--options', '-o', dest='kernel_options',
            default='', help=''.join(options_help_list))

        config_file_help_list = [
            "This specifies the configuration file to load into the ",
            "kernel before configuration."
            ]
        parser.add_option('--configuration', '-C', default='',
            help=''.join(config_file_help_list))

        """
        @todo Make this work correctly.

        editor_help_list = [
            "Specify the editor to use for editing the boot loader ",
            "configuration file after " + argv[0] + " has already ",
            "modified it.  The default editor is the one defined by ",
            "your ${EDITOR} environment variable."
            ]
        parser.add_option('--editor', '-e', 
            default=os.getenv("EDITOR", ""), 
            help=''.join(editor_help_list))
        """

        verbose_help_list = [
            "Sets verbose output."
            ]
        parser.add_option('--verbose', '-v', action='store_true',
            default=False, help=''.join(verbose_help_list))

        debug_help_list = [
            "Sets debugging output (implies verbose output)."
            ]
        parser.add_option('--debug', '-d', action='store_true',
            default=False, help=''.join(debug_help_list))

        quiet_help_list = [
            "Sets output to be a bit quieter.  If either debug or ",
            "verbose are set this option has no effect."
            ]
        parser.add_option('--quiet', '-q', action='store_true',
            default=False, help=''.join(quiet_help_list))

        rebuild_modules_help_list = [
            "Makes " + sys.argv[0] + " use module-rebuild to rebuild ",
            "the modules you have pulled in via portage for the new ",
            "kernel."
            ]
        parser.add_option('--rebuild-modules', '-r', action='store_true',
            default=False, dest='rebuild_modules',
            help=''.join(rebuild_modules_help_list))

        time_help_list = [
            "Times the actual build of the kernel allowing one to ",
            "determine if kernels are building faster based on ",
            "different aspects of the machine."
            ]
        parser.add_option('--time', '-t', action='store_true',
            dest='time_build', default=False,
            help=''.join(time_help_list))

        dry_run_help_list = [
            "Specifies that none of the actions that can modify the ",
            "filesystem should occur, but they should be printed to ",
            "the screen instead.  This way it can be seen what will ",
            "happen without actually doing it."
            ]
        parser.add_option('--dry-run', '-D', action='store_true', 
            dest='dry_run', default=False, 
            help=''.join(dry_run_help_list))

        remove_help_list = [
            "Will completely remove the specified kernel from the ",
            "system.  This will not remove the sources from the ",
            "world file."
            ]
        parser.add_option('--remove', '-R', action='store_true',
            dest='remove', default=False, 
            help=''.join(remove_help_list))

        version_help_list = [
            "Print version information about upkern."
            ]
        parser.add_option('--version', '-V', action='callback',
            callback=self._version, help=''.join(version_help_list))

        return parser.parse_args()

    def _version(self, option, opt_str, value, parser):
        print "upkern-3.1.2"
        sys.exit(0)

class UpkernException(Exception):
    def __init__(self, message, *args):
        super(UpkernException, self).__init__(args)
        self._message = message

    def GetMessage(self):
        return self._message

