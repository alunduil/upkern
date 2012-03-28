# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Alex Brandt <alunduil@alunduil.com>             
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

"""Upkern application class

This module provides the application class (for programmatic execution) for the
upkern application.

"""

import argparse

VERSION = "4.0.0"

class UpkernApplication(object):
    """Main application class for upkern."""

    def __init__(self, argv):
        self._debug = False
        self._verbose = False
        self._quiet = False

        arguments = UpkernOptions("upkern").parsed_args

        self._quiet = arguments.quiet
        self._debug = arguments.debug

        # If we have debugging turned on we should also have verbose.
        if self._debug: 
            self._verbose = True
        else: 
            self._verbose = arguments.verbose

        # If we have verbose we shouldn't be quiet.
        if self._verbose: 
            self._quiet = False

        # Other option handling ...
        helpers.COLORIZE = arguments.color

        self._configurator = variables.configurator
        self._rebuild_modules = variables.rebuild_modules
        self._time_build = variables.time_build
        self._kernel_options = variables.kernel_options
        self._configuration = variables.configuration
        self._dry_run = variables.dry_run
        self._remove = variables.remove

    def run(self):
        verbosity = {
                "debug": self._debug,
                "verbose": self._verbose,
                "quiet": self._quiet,
                "dry_run": self._dry_run,
                }

        kernel_params = {}
        kernel_params['configurator'] = self._configurator
        kernel_params['name'] = self._kernel
        kernel_params['rebuild_modules'] = self._rebuild_modules
        kernel_params['configuration'] = self._configuration
        kernel_params.update(verbosity)

        kernel = Kernel(**kernel_params)

        if self._remove:
            kernel.remove()
        else:
            kernel.configure()

            if self._time_build:
                start_time = time.time()

            kernel.build()

            if self._time_build:
                stop_time = time.time()

            kernel.install()

        bootloader_params = {}
        bootloader_params['kernel'] = kernel
        bootloader_params['kernel_options'] = self._kernel_options
        bootloader_params.update(verbosity)

        bootloader = BootLoader(**bootloader_params)
        
        if self._print_bootloader_configuration:
            helpers.colorize("GREEN", bootloader)

        bootloader.install_configuration()

        if self._editor:
            command_list = [
                self._editor,
                boot_loader.configuration_path
                ]
            os.system(" ".join(command_list))

        if self._time_build:
            hours = int((stop_time - start_time)/3600)
            minutes = int(((stop_time - start_time) % 3600)/60)
            seconds = int((stop_time - start_time) % 60)

            time_list = [
                    "The time to build the kernel was %02d:%02d:%02d.",
                    ] % (hours, minutes, seconds)

            for line in textwrap.wrap(''.join(time_list)):
                print line

        conclusion_list = [
                "The kernel, %s, has been successfully installed.  Please, ",
                "check that all configuration files are in the appropriate ",
                "place and that there are no errors in the boot loader ",
                "configuration.  It would be unfortunate if you were not able ",
                "to boo the kernel we just prepared.",
                ] % kernel.name

        for line in textwrap.wrap(''.join(conclusion_list)):
            print line

class UpkernOptions(object):
    """Options for the upkern application."""

    def __init__(self, name):
        """Create the option parser."""
        self._parser = argparse.ArgumentParser(prog = name)
        self._parser = self._add_args()

    @property
    def parser(self):
        """Return the option parser."""
        return self._parser

    @property
    def parsed_args(self):
        """Return the parsed arguments."""
        return self._parser.parse_args()

    def _add_args(self):
        """Add the options to the parser."""

        self._parser.add_argument("--version", action = "version", 
                version = "%(prog)s %(VERSION)s")

        # --verbose, -v
        help_list = [
                "Specifies verbose output from upkern.",
                ]
        self._parser.add_argument("--verbose", "-v", action = "store_true",
                default = "", help = "".join(help_list))

        # --debug, -D
        help_list = [
                "Specifies debugging output from upkern.  Implies verbose ",
                "output from upkern.",
                ]
        self._parser.add_argument("--debug", "-D", action = "store_true",
                default = False, help = "".join(help_list))

        # --quiet, -q
        help_list = [
                "Specifies quiet output from upkern.  This is superceded by ",
                "verbose output.",
                ]
        self._parser.add_argument("--quiet", "-q", action = "store_true",
                default = False, help = "".join(help_list))

        # --configurator, -c
        help_list = [
                "Specifies which configurator should be used to configure ",
                "the kernel sources.  The configurator can be on of the ",
                "following: ",
                ", ".join(kernel.configurators),
                ".  All the configurators are documented in the kernel ",
                "source files.",
                ]
        self._parser.add_argument("--configurator", "-c", 
                choices = kernel.configurators, default = "menuconfig",
                help = "".join(help_list))

        # --options, -o
        help_list = [
                "This string is literally tacked onto the kernel options ",
                "passed in by the bootloader.  This is where one would place ",
                "a framebuffer line or any other options to pass to the new ",
                "kernel."
                ]
        self._parser.add_argument("--options", "-o", dest = "kernel_options",
                default = "", help = "".join(help_list))

        # --config, -f
        help_list = [
                "Specifies the configuration file to load into the kernel ",
                "before running the configurator.",
                ]
        self._parser.add_argument('--config', '-f', defatul = "",
                help = "".join(help_list))

        # --rebuild-modules, -r
        help_list = [
                "Makes upkern use module-rebuild to rebuild the modules for ",
                "this new kernel (requires the module-rebuild use flag or a ",
                "separate install of module-rebuild)",
                ]
        self._parser.add_argument("--rebuild-modules", "-r", action = "store_true",
                default = False, dest = "rebuild_modules", 
                help = "".join(help_list))

        # --time, -t
        help_list = [
                "Times the actual build of the kernel.  Allows one to ",
                "determine if kernels are building faster based on different ",
                "configurations, etc."
                ]
        self._parser.add_argument("--time", "-t", action = "store_true", 
                default = False, help = "".join(help_list))

        # --dry-run, -d
        help_list = [
                "Specifies that none of the actions that can modify the ",
                "filesystem should occur but they should be printed to the ",
                "screen.  This way it can be seen what upkern will do ",
                "without actually doing it.",
                ]
        self._parser.add_argument("--dry-run", "-d", action = "store_true", 
                dest = "dry_run", defaults = False, help = "".join(help_list))

        return self._parser

