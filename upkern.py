#!/usr/bin/python

############################################################################
#    Copyright (C) 2007 by Alex Brandt                                     #
#    alunduil@alunduil.com                                                 #
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

## Description

"""
Python script that updates a kernel for the sysadmin in a way that is
conducive to the gentoo environment.
"""

import getopt
import os
import sys
from kernel import Kernel
from kernel.exceptions import *
from bootLoader import BootLoader
from bootLoader.exceptions import *
import time

def usage():
	print "usage: upkern [-m <method>] [-i <initrd file>] [-o <kernel options>] [-b <boot splash theme>] [-v[v]] [-h] [-r] [-e <editor>] [-s <sources>] [[-k] kernel]"
	sys.exit(0)

def help():
	print "Usage: upkern [options]... [kernel]"
	print "Automates the upgrade of a kernel. Including updating the information for boot"
	print "purposes in a grub or lilo configuration file."
	print ""
	print "Mandatory options for short options are mandatory for long options as well."
	print ""
	print "-m , --method=CONFIGURATOR       Specifies the configurator for the kernel."
	print "                                 Configurator can be one of the following:"
	print "                                 oldconfig, menuconfig, xconfig. All are the normal"
	print "                                 kernel configurators, and are documents in the"
	print "                                 source."
	print ""
	print "-i , --initrd=INITRDFILE         Specifies the initial ramdisk file to be used by"
	print "                                 the boot configuration. This option will be"
	print "                                 overruled by the -s/--splash-theme if it is"
	print "                                 specified."
	print ""
	print "-o , --kernel-opts=OPTIONS       Passes the string OPTIONS to the boot"
	print "                                 configuration. This is the place to pass the"
	print "                                 framebuffer line. One can use this or pass the"
	print "                                 option -e/--editor, and manually type it into the"
	print "                                 boot configuration file."
	print ""
	print "-b , --boot-splash-theme=THEME   Automatically makes sure that the necessary tools"
	print "                                 are installed, and then creates all the necessary"
	print "                                 system information to have a nice boot splash image"
	print "                                 on startup."
	print ""
	print "-v , --verbose                   Without this option or the -vv/--very-verbose"
	print "                                 option set there will be no output of the install"
	print "                                 or build progress of the kernel. With this option"
	print "                                 set the output will include errors, but not the"
	print "                                 standard build output."
	print ""
	print "-vv, --very-verbose              This option is similar to the -v/--verbose option."
	print "                                 This option will output everything from the build"
	print "                                 not just the errors or the necessary output."
	print ""
	print "-h , --help                      Brings up this help menu, and displays the"
	print "                                 the usage of some options that aren't quite"
	print "                                 obvious."
	print ""
	print "-r , --rebuild-modules           Tells the program to rebuild the modules that you"
	print "                                 have emerged into your system. Examples of these"
	print "                                 include nvidia-drivers, alsa-drivers, svgalib, and"
	print "                                 others. This option takes advantage of the"
	print "                                 module-rebuild script that one can emerge, and will"
	print "                                 not work without it."
	print ""
	print "-e , --editor=EDITOR             Brings up the configuration file in an editor after"
	print "                                 it has been modified by the script so that you may"
	print "                                 verify the modifications, and make your own if you"
	print "                                 wish to do so. EDITOR is the full path to the"
	print "                                 editor you wish to utilize."
	print ""
	print "-s , --sources=SOURCES           The sources you wish to use (if you need to specify"
	print "                                 a set, or if you wish to use multiple sources on the"
	print "                                 same machine."
	print ""
	print "-k , --kernel=KERNEL             The kernel you wish to build. This does not have to"
	print "                                 be specified, but if it is the version number must"
	print "                                 be specified at the very least. If the kernel is"
	print "                                 not specified the highest version kernel already"
	print "                                 installed will be used."
	sys.exit(0)

def main():
	if os.getuid() == 0:
		shortOptions    =   'm:i:o:s:k:b:vhre:'
		longOptions     =   ['method=', 'initrd=', 'kernel-opts=', 'boot-splash-theme=', 'verbose', 'very-verbose', 'help', 'rebuild-modules', 'editor=', 'kernel=', 'sources=']
		verbosity       =   0
		rebuildModules  =   False
		sources         =   ""
		buildMethod     =   "menuconfig"
		kernelName      =   ""
		splashTheme	=   ""
		initrd		=   ""
		kernelOptions	=   ""

		try:
			optionList, arguments = getopt.gnu_getopt( sys.argv[1:], shortOptions, longOptions )
		except:
			usage()

		for option in optionList:
			if option[0] == '-m' or option[0] == '--method':
				buildMethod = option[1]
			elif option[0] == '-i' or option[0] == '--initrd':
				initrd = option[1]
			elif option[0] == '-o' or option[0] == '--kernel-opts':
				kernelOptions = option[1]
			elif option[0] == '-s' or option[0] == '--sources':
				sources = option[1]
			elif option[0] == '-v':
				verbosity = verbosity + 1
			elif option[0] == '-h' or option[0] == '--help':
				help()
			elif option[0] == '-r' or option[0] == '--rebuild-modules':
				rebuildModules = True
			elif option[0] == '-e' or option[0] == '--editor':
				editor = option[1]
			elif option[0] == '-b' or option[0] == '--boot-splash-theme':
				splashTheme = option[1]
			elif option[0] == '--very-verbose':
				verbosity = 2
			elif option[0] == '--verbose':
				verbosity = 1

		if len(arguments) != 0:
			kernelName = arguments[0]

		try:
			kernel = Kernel(kernelName, sources, rebuildModules, buildMethod)
		except RootNotFoundError, rootNotFoundError:
			print rootNotFoundError
			return
		except FstabReadError, fstabReadError:
			print fstabReadError
			return
		except BadKernelError, badKernelError:
			print badKernelError
			return
		except KernelNotFoundError, kernelNotFoundError:
			print kernelNotFoundError
			return
		except KernelMaskedError, kernelMaskedError:
			print kernelMaskedError
			return
		except BadSourceTypeError, badSourceTypeError:
			print badSourceTypeError
			return
		except BogusSourceTypeError, bogusSourceTypeError:
			print bogusSourceTypeError
			return

		# The kernel is now ready to go. Let's configure the options.
		try:
			kernel.configure(verbosity)
		except SourceAccessDeniedError, sourceAccessDeniedError:
			print sourceAccessDeniedError
			return
		except BadConfiguratorError, badConfiguratorError:
			print badConfiguratorError
			return

		# The kernel is now configured. Let's build the thing.
		try:
			startTime = time.time()
			kernel.build(verbosity)
			finishTime = time.time()
		except SourceAccessDeniedError, sourceAccessDeniedError:
			print sourceAccessDeniedError
			return

		# Install the bits of the kernel where they should go.
		try:
			kernel.install()
		except SourceAccessDeniedError, sourceAccessDeniedError:
			print sourceAccessDeniedError
			return

		# Create the bootloader.
		try:
			bootLoader = BootLoader(kernel.kernelImage, kernel.rootPartition, splashTheme, initrd, kernelOptions)
		except BootLoaderError, bootLoaderError:
			print bootLoaderError
			return
		except BootNotFoundError, bootNotFoundError:
			print bootNotFoundError
			return
		except FstabReadError, fstabReadError:
			print fstabReadError
			return

		# Create the configuration file.
		bootLoader.createConfiguration()

		# Install the configuration file.
		bootLoader.installConfiguration()

	else:
		print "You must be root to run this program."

main()
