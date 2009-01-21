#!/usr/bin/env python

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

"""Kernel update automater for Gentoo.

Python script that updates a kernel for the sysadmin in a way that is
conducive to the Gentoo environment. This script will only work on a system
that has portage installed, but should only raise a warning if other
non-necessary modules from the portage system are utilized.

"""

import optparse
import sys
import textwrap
import time

from kernel import *
from bootloader import *

def main():
    if os.getuid() != 0:
        print "Superuser access is required!"
        return 1;

    usage = "usage: %prog [options] kernel"

    parser = optparse.OptionParser(usage=usage)

    configurators = [
        "menuconfig",
        "xconfig",
        "gconfig",
        "oldconfig",
        "silentoldconfig",
        "defconfig",
        "allyesconfig",
        "allmodconfig",
        "allnoconfig",
        "randconfig"
        ]

    configurator_help_list = [
        "Specifies which configurator should be used to configure the kernel",
        " sources. The configurator can be one of the following: ",
        ", ".join(configurators),
        " All the configurators are documented in the kernel source files."
        ]
    parser.add_option('--configurator', '-c', type='choice',
        choices=configurators, default='menuconfig',
        help=''.join(configurator_help_list))

    initrd_help_list = [
        "Specifies the initial ramdisk file to the boot loader configuration."
        ]
    parser.add_option('--initrd', '-i', default='',
        help=''.join(initrd_help_list))

    options_help_list = [
        "This string is literally tacked on to the kernel line in your boot",
        " loader's configuration. This is the place you would want to stick",
        " a framebuffer line, or any other options you want your kernel to",
        " have."
        ]
    parser.add_option('--options', '-o', dest='kernel_options', default='',
        help=''.join(options_help_list))

    boot_splash_help_list = [
        "Verifies the splash-utils are installed, and sets up the specified",
        " boot splash theme to work on boot."
        ]
    parser.add_option('--boot-splash', '-b', dest='boot_splash', default='',
        help=''.join(boot_splash_help_list))

    sources_help_list = [
        "Specify the sources that will by used for this kernel build. If not",
        " specified, the gentoo sources will be used."
        ]
    parser.add_option('--sources', '-s', default='gentoo',
        help=''.join(sources_help_list))

    editor_help_list = [
        "Specify the editor to use for editing the boot loader configuration",
        " file after " + sys.argv[0] + " has already modified it. The",
        " default editor is the one defined by your ${EDITOR} environment",
        " variable."
        ]
    parser.add_option('--editor', '-e', help=''.join(editor_help_list))

    verbose_help_list = [
        "Sets the verbosity level, and how many messages are printed out as ",
        sys.argv[0] + " runs. The levels are: none, error, warning, and",
        " debug. To set the level specify multiple -v, or --verbose flags.",
        " By setting the level, you are specifying the highest level",
        " that will be printed to the standard output."
        ]
    parser.add_option('--verbose', '-v', action='count', dest='verbosity',
        help=''.join(verbose_help_list))

    rebuild_modules_help_list = [
        "Makes " + sys.argv[0] + " use module-rebuild to rebuild the modules",
        " you have pulled in via portage for the new kernel."
        ]
    parser.add_option('--rebuild-modules', '-r', action='store_true',
        default=False, dest='rebuild_modules',
        help=''.join(rebuild_modules_help_list))

    time_help_list = [
        "Times the actual build of the kernel allowing one to determine if",
        " kernels are building faster based on different aspects of the",
        " machine."
        ]
    parser.add_option('--time', '-t', action='store_true', dest='time_build',
        default=False, help=''.join(time_help_list))

    kernel_help_list = [
        "Specifies a varying amount of information about the kernel you",
        " would like to build. Ranges from kernel version to the full gentoo",
        " specification."
        ]
    parser.add_option('--kernel', '-k', dest='kernel_name', default="",
        help=''.join(kernel_help_list))

    version_help_list = [
        "Specifies the currently installed version of upkern."
        ]
    parser.add_option('--version', '-V', action='store_true', dest='version',
        default=False, help=''.join(version_help_list))

    options, arguments = parser.parse_args()

    if len(arguments) != 0:
        kernel_name = arguments[0]
    else:
        kernel_name = ""

    if options.version:
        print "upkern, version 2.0.9"
        sys.exit(0)

    try:
        kernel = Kernel(options.configurator, options.kernel_name or \
            kernel_name, options.sources, options.rebuild_modules, options.boot_splash)
        kernel.configure(options.verbosity)
        if (options.time_build): start_time = time.time()
        kernel.build(options.verbosity)
        if (options.time_build): stop_time = time.time()
        kernel.install(options.verbosity)

        boot_loader = create_bootloader(kernel, options.kernel_options,
            options.initrd, options.boot_splash)
        boot_loader.create_configuration()
        boot_loader.install_configuration()

        if options.editor:
            if len(options.editor) <= 0:
                options.editor = os.getenv("EDITOR", "")
            os.system(options.editor + " " + boot_loader.config)

        print "The kernel has been successfully upgraded to " + \
            kernel.name + ".\n"
        if (options.time_build):
            print "The time to build the kernel was %(time).2f s\n" % \
                {'time': stop_time - start_time}
        output_list = [
            "Please, check that all config files are in the appropriate",
            " place, and that there are no errors in the configuration of",
            " the boot process. It would be unfortunate if you were not able",
            " to boot the new kernel we just prepared."
            ]
        for string in textwrap.wrap(''.join(output_list)):
            print string
    except KernelException, error:
        error.print_message()
    except BootLoaderException, error:
        error.print_message()

    sys.exit(0)

if __name__ == '__main__':
    main()
