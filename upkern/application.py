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
import datetime

import upkern.helpers as helpers
import upkern.kernel as kernel
from upkern.bootloader import BootLoader

class UpkernApplication(object): #pylint: disable-msg=R0903
    """Main application class for upkern."""

    def __init__(self):
        self._debug = False
        self._verbose = False
        self._quiet = False

        self.arguments = UpkernOptions("upkern").parsed_args

        # If we have debugging turned on we should also have verbose.
        if self.arguments.debug: 
            self.arguments.verbose = True

        # If we have verbose we shouldn't be quiet.
        if self.arguments.verbose: 
            self.arguments.quiet = False

        # Other option handling ...
        helpers.COLORIZE = self.arguments.color

    def run(self):
        """Does all the legwork of getting the specified kernel installed."""
        verbosity = {
                "debug": self.arguments.debug,
                "verbose": self.arguments.verbose,
                "quiet": self.arguments.quiet,
                "dry_run": self.arguments.dry_run,
                }

        kernel_params = {
                "name": self.arguments.name,
                }
        kernel_params.update(verbosity)

        sources = kernel.Sources(**kernel_params)
        sources.prepare(configuration = self.arguments.config)
        sources.configure(configurator = self.arguments.configurator)

        if self.arguments.time:
            start = datetime.datetime.now()

        binary = sources.build()

        if self.arguments.time:
            delta = datetime.datetime.now() - start

        if self.arguments.rebuild_modules:
            sources.rebuild_modules()

        binary.install()

        bootloader_params = {}
        bootloader_params.update(verbosity)

        bootloader = BootLoader(**bootloader_params)
        
        bootloader.prepare(kernel = binary,
                kernel_options = self.arguments.kernel_options)

        bootloader.install()

        if not self.arguments.quiet:
            conclusion_list = [
                    "The kernel, {name}, has been successfully installed.  ".format(
                        name = binary.name),
                    "Please, check that all configuration files are ",
                    "installed correctly and the bootloader is configured ",
                    "correctly.  ",
                    ]

            if self.arguments.time:
                conclusion_list.extend([
                    "The kernel's build time was {delta!s}".format(delta = delta),
                    ])

            print("".join(conclusion_list))

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
                version = "%(prog)s 4.0.0")

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
        
        # --color=[none,light,dark,auto]
        help_list = [
                "Specifies whether output should use color and which type of ",
                "background to color for (light or dark).  This defaults to ",
                "auto.",
                ]
        self.parser.add_argument("--color", 
                choices = ["none", "light", "dark", "auto"], default = "auto",
                help = "".join(help_list))

        # --dry-run, -d
        help_list = [
                "Specifies that none of the actions that can modify the ",
                "filesystem should occur but they should be printed to the ",
                "screen.  This way it can be seen what upkern will do ",
                "without actually doing it.",
                ]
        self._parser.add_argument("--dry-run", "-d", action = "store_true", 
                dest = "dry_run", default = False, help = "".join(help_list))

        # --configurator, -c
        configurators_list = [
                "config",
                "menuconfig",
                "nconfig",
                "xconfig",
                "gconfig",
                "oldconfig",
                "silentoldconfig",
                "defconfig",
                "${PLATFORM}_defconfig",
                "allyesconfig",
                "allmodconfig",
                "allnoconfig",
                "randconfig",
                ]
        help_list = [
                "Specifies which configurator should be used to configure ",
                "the kernel sources.  The configurator can be on of the ",
                "following: ",
                ", ".join(configurators_list),
                ".  All the configurators are documented in the kernel ",
                "source files.",
                ]
        self._parser.add_argument("--configurator", "-c", 
                choices = configurators_list, default = "menuconfig",
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
        self._parser.add_argument('--config', '-f', default = "",
                help = "".join(help_list))

        # --rebuild-modules, -r
        help_list = [
                "Makes upkern use module-rebuild to rebuild the modules for ",
                "this new kernel (requires the module-rebuild use flag or a ",
                "separate install of module-rebuild).  If module-rebuild is ",
                "not available; this results in a no-op and no harm is done. ",
                ]
        self._parser.add_argument("--rebuild-modules", "-r",
                action = "store_true", default = False,
                dest = "rebuild_modules", help = "".join(help_list))

        # --time, -t
        help_list = [
                "Times the actual build of the kernel.  Allows one to ",
                "determine if kernels are building faster based on different ",
                "configurations, etc."
                ]
        self._parser.add_argument("--time", "-t", action = "store_true", 
                default = False, help = "".join(help_list))

        # [name]
        help_list = [
                "The name of the kernel (using ebuild conventions) to build.",
                ]
        self._parser.add_argument("name", nargs = "?", default = "",
                help = "".join(help_list))

        return self._parser

