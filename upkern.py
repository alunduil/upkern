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

import getopt
import sys
from textwrap import wrap
import time

from kernel import *
from bootloader import *

def usage(name):
    """Prints out the usage of the utility.

    Passes the usage string to the user, and then terminates the program.

    """
    usage_list = [
        "usage: " + name,
        " [-c configurator]",
        " [-i initrd]",
        " [-o kernel options]",
        " [-b bootsplash theme]",
        " [-s sources]",
        " [-e editor]",
        " [-v level]",
        " [-r]",
        " [-t]",
        " [-h]",
        " [[-k] kernel]"
        ]
    print ''.join(usage_list)

def help(name):
    """Prints out the help menu for the utility.

    Passes the help menu string to the user in groups of 70 characters at a time.

    """
    print "Usage: " + name + " [options] ... [kernel]"

    help_list = [
        "Automates the updating of a Gentoo kernel, and will even attempt to",
        " download sources that are not present on your machine if so",
        " instructed. The script should be able to handle anything you throw",
        " at it, but it can't always read your mind. For usability",
        " suggestions or comments, please, contact the author with",
        " appropriate feedback"
        ]
    for string in wrap(''.join(help_list)):
        print string
    print ""

    help_list = [
        "Mandatory options for short options are mandatory for long options",
        " as well."
        ]
    for string in wrap(''.join(help_list)):
        print string
    print ""

    help_list = [
        "-c, --configurator=CONFIGURATOR\tSpecifies which configurator",
        " should be"
    ]
    print ''.join(help_list)
    print "\t\t\t\tused to configure the kernel sources."
    print "\t\t\t\tThe CONFIGURATOR can be one of the"
    print "\t\t\t\tfollowing: oldconfig, menuconfig,"
    print "\t\t\t\txconfig, etc. All the configurators"
    print "\t\t\t\tare documented in the kernel source"
    print "\t\t\t\tfiles."
    print ""

    print "-i, --initrd=INITRD\t\tSpecifies the initial ramdisk file to"
    print "\t\t\t\tthe boot loader configuration."
    print ""

    print "-o, --options=OPTIONS\t\tThis string is literally tacked on to"
    print "\t\t\t\tthe kernel line in your boot loader's"
    print "\t\t\t\tconfiguration. This is the place you"
    print "\t\t\t\twould want to stick a framebuffer"
    print "\t\t\t\tline, or any other options you want"
    print "\t\t\t\tyour kernel to have."
    print ""

    print "-b, --boot-splash=THEME\t\tVerifies the splash-utils are"
    print "\t\t\t\tinstalled, and uses the THEME"
    print "\t\t\t\tspecified."
    print ""

    print "-s, --sources=SOURCES\t\tSpecify the sources that will by used"
    print "\t\t\t\tfor this kernel build. If not"
    print "\t\t\t\tspecified, the gentoo sources will be"
    print "\t\t\t\tused."
    print ""

    print "-e, --editor=EDITOR\t\tSpecify the editor to use for editing"
    print "\t\t\t\tthe boot loader configuration"
    print "\t\t\t\tfile after " + name + " has"
    print "\t\t\t\talready modified it. The"
    print "\t\t\t\tdefault editor is the one"
    print "\t\t\t\tdefined by your ${EDITOR}"
    print "\t\t\t\tenvironment variable."
    print ""

    print "-v, --verbose=LEVEL\t\tSets the verbosity level, and how many"
    print "\t\t\t\tmessages are printed out as"
    print "\t\t\t\t" + name + " runs. The values for"
    print "\t\t\t\tLEVEL are: none, error, warning,"
    print "\t\t\t\tand debug. By setting the level,"
    print "\t\t\t\tyou are specifying the highest"
    print "\t\t\t\tlevel that will be printed to the"
    print "\t\t\t\tstandard output."
    print ""

    print "-r, --rebuild-modules\t\tMakes " + name + " use module-rebuild"
    print "\t\t\t\tto rebuild the modules you have"
    print "\t\t\t\tpulled in via portage for the new"
    print "\t\t\t\tkernel."
    print ""

    print "-t, --time\t\t\tTimes the actual build of the kernel allowing"
    print "\t\t\t\tone to determine if kernels are building faster or"
    print "\t\t\t\tbased on different aspects of the machine."
    print ""

    print "-h, --help\t\t\tPrints out this help menu."
    print ""

    print "-k, --kernel=KERNEL\t\tSpecifies a varying amount of information"
    print "\t\t\t\tabout the kernel you would like to"
    print "\t\t\t\tbuild. Ranges from kernel version"
    print "\t\t\t\tto the full gentoo specification."

def main():
    if os.getuid() != 0:
        print "Superuser access is required!"
        return 1;

    short_options = "c:i:o:b:s:e:vrthk:"
    long_options = ['configurator=', 'initrd=', 'options=', 'boot-splash=',
        'sources=', 'editor=', 'verbose=', 'rebuild-modules', 'time', 'help',
        'kernel=']

    configurator = 'menuconfig'
    initrd = ''
    kernel_options = ''
    boot_splash = ''
    sources = 'gentoo'
    editor = os.getenv("EDITOR", "")
    edit = False
    verbosity = 0
    rebuild_modules = False
    time_build = False
    kernel_name = ""

    try:
        options, arguments = getopt.gnu_getopt(sys.argv[1:], short_options, long_options)
    except:
        usage(sys.argv[0])
        sys.exit(1)

    for option in options:
        if option[0] == '-c' or option[0] == '--configurator':
            configurator = option[1]
        elif option[0] == '-i' or option[0] == '--initrd':
            initrd = option[1]
        elif option[0] == '-o' or option[0] == '--options':
            kernel_options = option[1]
        elif option[0] == '-b' or option[0] == '--boot-splash':
            boot_splash = option[1]
        elif option[0] == '-s' or option[0] == '--sources':
            sources = option[1]
        elif option[0] == '-e' or option[0] == '--editor':
            if len(option[1]) > 0:
                editor = option[1]
            edit = True
        elif option[0] == '-v':
            verbosity += 1
        elif option[0] == '--verbose':
            if option[1].lower() == "none":
                verbosity = 0
            elif option[1].lower() == "error":
                verbosity = 1
            elif option[1].lower() == "warning":
                verbosity = 2
            elif option[1].lower() == "debug":
                verbosity = 3
            else: pass
        elif option[0] == '-r' or option[0] == '--rebuild-modules':
            rebuild_modules = True
        elif option[0] == '-t' or option[0] == '--time':
            time_build = True
        elif option[0] == '-h' or option[0] == '--help':
            help(sys.argv[0])
            sys.exit(0)
        elif option[0] == '-k' or option[0] == '--kernel':
            kernel_name = option[1]

    if len(arguments) != 0:
        kernel_name = arguments[0]

    try:
        kernel = Kernel(configurator, kernel_name, sources, rebuild_modules)
        kernel.configure(verbosity)
        if (time_build): start_time = time.clock()
        kernel.build(verbosity)
        if (time_build): stop_time = time.clock()
        kernel.install(verbosity)

        boot_loader = create_bootloader(kernel, kernel_options, initrd, boot_splash)
        boot_loader.create_configuration()
        boot_loader.install_configuration()

        if edit and len(editor) > 0:
            os.system(editor + " " + boot_loader.config)

        print "The kernel has been successfully upgraded to " + kernel.name + ".\n"
        if (time_build):
            print "The time to build the kernel was " + str(stop_time - \
                start_time) + "s.\n"
        output_list = [
            "Please, check that all config files are in the appropriate place,",
            " and that there are no errors in the configuration of the boot",
            " process. It would be unfortunate if you were not able to boot the",
            " new kernel we just prepared."
            ]
        for string in wrap(''.join(output_list)):
            print string
    except KernelException, error:
        error.print_message()
    except BootLoaderException, error:
        error.print_message()

    sys.exit(0)

main()
