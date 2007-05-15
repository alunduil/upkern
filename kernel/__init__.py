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

import os
import re
import exceptions
import operator
import shutil

## Kernel Class Definition:

class Kernel:

	# Kernel class constructor ================================================
	# Function:         Get the information about the system necessary of a
	#                   kernel.
	# PreConditions:
	# PostConditions:   Kernel is initialized, and the information is
	#                   populated.
	# Returns:          Object kernel.
	# -------------------------------------------------------------------------

	def __init__(self, kernelName = "", sources = "", rebuildModules = True, buildMethod = "menuconfig"):
		self.installCount	= 0					# Zero the install count.
		self.kernelName		= kernelName		# Name of the kernel.
		self.rebuildModules	= rebuildModules	# Whether to rebuild the
												# modules in the system.
		self.sources		= sources			# Sources to use.
		self.buildMethod	= buildMethod		# Build Method to use.

		# Get the root partition for the system.
		self.determineRoot()

		# Get the architecture of the system.
		self.determineArch()

		# Check for an old symlink.
		self.checkSymlink()

		# Get the name of the kernel.
		if len(self.kernelName) != 0:
			self.setKernelName()

		# Download the sources if necessary.
		if not self.areSourcesDownloaded():
			self.download()

		# Create a symlink to the new source directory.
		self.setSymlink()

		# Copy the most recent configuration file to the source directory.
		self.copyConfig()

	# Kernel class round trip string ==========================================
	# Function:         Create a string that goes back and forth like some sort
	#                   of cyclic trip thing.
	# PreConditions:    An object exists, and the programmer calls this method.
	# PostConditions:   A string that is mainly used for debugging purposes,
	#                   and hopefully allows the programmer to know what is
	#                   going on somewhere even if it isn't in this class.
	# Returns:          A string that can be parsed.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# Kernel class string return ==============================================
	# Function:         Create a string that the user might like to see.
	# PreConditions:    Does the user care?
	# PostConditions:   Hope that showed him. Now, back to important things.
	# Returns:          The name of the kernel. ... What are you doing here?
	#                   Go away. I don't like you.
	# -------------------------------------------------------------------------

	def __str__(self):
		return self.kernelName

	# setRoot() ===============================================================
	# Function:         Get the device that the root partition is mounted on.
	# PreConditions:
	# PostConditions:   The device of the root partition is stored in
	#                   self.rootPartition.
	# Returns:
	# -------------------------------------------------------------------------

	def determineRoot(self):
		rootExpression = re.compile('^(/dev/\w+)\s+/\s+.+$', re.IGNORECASE)

		if os.access('/etc/fstab', os.F_OK):
			fstab = open('/etc/fstab', 'r')
			for line in fstab:
				if rootExpression.match(line):
					self.rootPartition = rootExpression.match(line).group(1)
					fstab.close()
					break
			else:
				raise exceptions.RootNotFoundError
				fstab.close()
		else:
			raise exceptions.FstabReadError
			fstab.close()
		return

	# isBootMounted() ===========================================================
	# Function:         Determine whether the boot partition is already
	#                   mounted.
	# PreConditions:
	# PostConditions:   A boolean (self.isBootMounted) of whether the /boot
	#                   partition is mounted is set.
	# Returns:
	# -------------------------------------------------------------------------

	def isBootMounted(self):
		bootFiles = os.listdir('/boot/')

		for file in bootFiles:
			if file != "boot":
				return True
		return False

	# checkSymlink() ==========================================================
	# Function:         Check if the kernel symlink exists, and deletes it.
	# PreConditions:
	# PostConditions:   The symlink: /usr/src/linux will be removed.
	# Returns:
	# -------------------------------------------------------------------------

	def checkSymlink(self):
		if os.path.islink('/usr/src/linux'):
			os.remove('/usr/src/linux')
		return

	# setKernelName() =========================================================
	# Function:         Grabs the kernel name to be used by the system.
	# PreConditions:
	# PostConditions:   The name of the kernel on the system is housed in
	#                   self.kernelName.
	# Returns:
	# -------------------------------------------------------------------------

	def setKernelName(self):
		if os.access('/usr/src/', os.F_OK):
			sourceList = []
			sourceListFull = []
			program = os.popen("emerge -s --quiet sources 2> /dev/null", "r")

			sourceExpression1 = re.compile('^.+sys-kernel/(?P<sourceType>\S+)-sources\s+$')
			sourceExpression2 = re.compile('^.+sys-kernel/(?P<sourceType>\S+)-sources.+$')

			for line in program.readlines():
				match = sourceExpression1.match(line)
				match2 = sourceExpression2.match(line)
				if match:
					sourceList.append(match.group("sourceType"))
					sourceListFull.append(match.group("sourceType"))
				elif match2:
					sourceListFull.append(match2.group("sourceType"))

			kernelExpression = re.compile('^(?P<version>((\d+\.){2}\d+))(-(?P<sourceType>.+?))?(?P<release>-r\d+)?$')
			packageExpression = re.compile('^((?P<sourceType>.+?)-)?(sources-)?(?P<version>((\d+\.){2}\d+))(?P<release>-r\d+)?$')

			match = kernelExpression.match(self.kernelName) or packageExpression.match(self.kernelName)
			if match and match.group("sourceType"):
				for sourceType in sourceList:
					if match.group("sourceType") == sourceType:
						break
				else:
					for sourceType in sourceListFull:
						if match.group("sourceType") == sourceType:
							raise exceptions.BadSourceTypeError(match.group("sourceType"))
					else:
						raise exceptions.BogusSourceTypeError(match.group("sourceType"))
			elif not match:
				raise exceptions.BadKernelError

			self.downloadName = (match.group("sourceType") or self.sources or "gentoo") + "-sources-" + match.group("version") + (match.group("release") or "")
			self.kernelName = "linux-" + match.group("version") + "-" + (match.group("sourceType") or self.sources or "gentoo") + (match.group("release") or "")
		return

	# areSourcesDownloaded() ==================================================
	# Function:         Checks if the kernel sources are downloaded for us.
	# PreConditions:    What's a kernel?
	# PostConditions:   Where do we get it?
	# Returns:          Do we have a kernel? What do we do now?
	# -------------------------------------------------------------------------

	def areSourcesDownloaded(self):
		hiddenDirectoryExpression = re.compile('^\..+$')

		directories = os.listdir('/usr/src/')
		directories.sort(reverse=True)

		for directory in directories:
			match = hiddenDirectoryExpression.match(directory)
			if not match:
				if len(self.kernelName) == 0:
					self.kernelName = directory
				if self.kernelName == directory:
					return True
		return False

	# download() ==============================================================
	# Function:         Downloads the kernel sources since you obviously
	#                   couldn't accomplish this.
	# PreConditions:    It's nice to check that the kernel isn't already there
	#                   wasted cycles is wasted life, and last I heard life was
	#                   good. That doesn't make sense, oh well.
	# PostConditions:   Good your kernel has been downloaded, please run
	#                   don't do anything more you're in my hands now...
	# Returns:          Mwahahahahaha...
	# -------------------------------------------------------------------------

	def download(self):
		emergeSearch = os.popen('emerge -p =' + self.downloadName, 'r')

		emergeErrorExpression1 = re.compile('^emerge: there are no ebuilds to satisfy.+$')
		emergeErrorExpression2 = re.compile('^.+masked by:\s(?P<keyword>.+?)\s.+$')

		for line in emergeSearch.readlines():
			match1 = emergeErrorExpression1.match(line)
			match2 = emergeErrorExpression2.match(line)
			if match1:
				raise exceptions.KernelNotFoundError(self.downloadName)
				break
			elif match2:
				raise exceptions.KernelMaskedError(self.downloadName, match2.group("keyword"))
				break
		else:
			os.system('emerge -v =' + self.downloadName)
		return

	# setSymlink() ============================================================
	# Function:         Creates a new symlink to the newly selected kernel
	#                   sources.
	# PreConditions:    The old symlink is destroyed which is what
	#                   checkSymlink() does for us.
	# PostConditions:   The new symlink will be setup and ready to go.
	# Returns:          Happiness.
	# -------------------------------------------------------------------------

	def setSymlink(self):
		os.symlink('/usr/src/' + self.kernelName, '/usr/src/linux')
		return

	# copyConfig() ============================================================
	# Function:         Copy the most recent configuration file from /boot to
	#                   /usr/src/linux/.config.
	# PreConditions:    A configuration file exists in /boot, otherwise the
	#                   default configuration file for the kernel will be used.
	# PostConditions:   The configuration file has been loaded for the build
	#                   process.
	# Returns:          Nothing...you want to fight about it?
	# -------------------------------------------------------------------------

	def copyConfig(self):
		if self.isBootMounted():
			configExpression = re.compile('^/boot/config-.+$')

			directories = os.listdir('/boot')
			directories.sort(reverse=True)

			for directory in directories:
				match = configExpression.match(directory)

				if match:
					shutil.copy(match.group(), '/usr/src/.config')
					break
		else:
			os.system('mount /boot')
			self.copyConfig()
			os.system('umount /boot')
		return

	# cwdSource() =============================================================
	# Function:         Get into the kernel's source directory.
	# PreConditions:    No walls.
	# PostConditions:   We are in the kernel source, he he he.
	# Returns:          Nothing
	# -------------------------------------------------------------------------

	def cwdSource(self):
		os.chdir('/usr/src/linux')

		directoryExpression = re.compile('^/usr/src/linux.+$')

		match = directoryExpression.match(os.getcwd())

		if not match:
			raise exceptions.SourceAccessDeniedError
		return

	# getMakeOpts() ===========================================================
	# Function:         Find out how many jobs this Gentoo wants.
	# PreConditions:    You have the file /etc/make.conf right?
	# PostConditions:   Your kernel build fast man...
	# Returns:          The fast way to do things.
	# =========================================================================

	def getMakeOpts(self):
		makeExpression = re.compile('^MAKEOPTS="(?P<makeOpts>.+?)"$')

		makeOutput = os.popen('fgrep MAKEOPTS /etc/make.conf', 'r')

		match = makeExpression.match(makeOutput.readline())

		if not match:
			exceptions.NoMakeOptError noMakeOptError()
			print noMakeOptError
			return "-j1"

		return match.group("makeOpts")

	# configure() =============================================================
	# Function:         Configure the kernel for your system with the method
	#                   you choose.
	# PreConditions:    Nadda, you don't have to do anything.
	# PostConditions:   Your kernel is configured begin make now.
	# Returns:          A configuration.
	# =========================================================================

	def configure(self, verbosity):
		self.cwdSource()
		makeOpts = self.getMakeOpts()

		methodExpression = re.compile('^(menuconfig|xconfig|gconfig|oldconfig|silentoldconfig|defconfig|allyesconfig|allmodconfig|allnoconfig|randconfig)$')
		outputExpression = re.compile('^(menuconfig|oldconfig|silentoldconfig)$')

		match1 = methodExpression.match(self.buildMethod)
		match2 = outputExpression.match(self.buildMethod)

		if match1:
			if verbosity <= 0:
				if match2:
					os.system('make -s ' + makeOpts + ' ' + self.buildMethod + ' 2>/dev/null')
				else:
					os.system('make ' + makeOpts + ' ' + self.buildMethod + '>/dev/null 2>/dev/null')
			elif verbosity == 1:
				os.system('make ' + makeOpts + ' ' + self.buildMethod + ' 2>/dev/null')
			elif verbosity >= 2:
				os.system('make ' + makeOpts + ' ' + self.buildMethod)
		elif len(self.buildMethod) == 0:
			if verbosity <= 0:
				os.system('make -s ' + makeOpts + ' menuconfig 2>/dev/null')
			elif verbosity == 1:
				os.system('make ' + makeOpts + ' menuconfig 2>/dev/null')
			elif verbosity >= 2:
				os.system('make ' + makeOpts + ' menuconfig')
		else:
			raise exceptions.BadConfiguratorError(self.buildMethod)
		return

	# setArch() ===============================================================
	# Function:         Get the architecture of the machine we are working on.
	# PreConditions:    Your machine is built right?
	# PostConditions:   We now know what your machine is.
	# Returns:          Architecture.
	# -------------------------------------------------------------------------

	def determineArch(self):
		self.archName = os.popen('uname -m', 'r').readline().strip()
		return

	# build() =================================================================
	# Function:         Build the kernel. Why just let it sit there?
	# PreConditions:    Do we have the proper sources? Hopefully, this kernel
	#                   things made sure the environment was properly setup.
	# PostConditions:   The kernel is build, and ready to move into your
	#                   system.
	# Returns:          A built kernel image.
	# -------------------------------------------------------------------------

	def build(self, verbosity):
		self.cwdSource()
		makeOpts = self.getMakeOpts()

		kernelExpression = re.compile('^.+(?P<version>\d+\.\d+)\..+$')

		version = kernelExpression.match(self.kernelName).group("version")

		if verbosity >= 2:
			output = ''
		elif verbosity == 1:
			output = '2>/dev/null'
		elif verbosity <= 0:
			output = '>/dev/null 2>/dev/null'
		if version == "2.4":
			if self.archName == "sparc32":
				os.system('make ' + makeOpts + ' dep' + output + '&& make ' + makeOpts + ' clean vmlinux modules modules_install' + output)
			elif self.archName == "sparc64":
				os.system('make ' + makeOpts + ' dep' + output + '&& make ' + makeOpts + ' clean vmlinux image modules modules_install' + output)
			else:
				os.system('make ' + makeOpts + ' dep' + output + '&& make ' + makeOpts + ' bzImage modules modules_install' + output)
		elif version == "2.6":
			if self.archName == "sparc64":
				os.system('make ' + makeOpts + ' ' + output + '&& make ' + makeOpts + ' image modules_install' + output)
			else:
				os.system('make ' + makeOpts + ' ' + output + '&& make ' + makeOpts + ' modules_install' + output)
		if self.rebuildModules:
			os.system('module-rebuild -X rebuild' + output)
		return

	# install() ===============================================================
	# Function:         Install the proper files into /boot.
	# PreConditions:    The kernel has been built, and is ready to be
	#                   installed.
	# PostConditions:   The kernel is installed.
	# Returns:          Nothing.
	# -------------------------------------------------------------------------

	def install(self):
		self.cwdSource()

		kernelExpression = re.compile('^.+(?P<version>\d+\.\d+)\..+$')
		archExpression = re.compile('^i\d86$')

		version = kernelExpression.match(self.kernelName).group("version")
		match = archExpression.match(self.archName)

		if self.isBootMounted():
			if match:
				shutil.copy('arch/i386/boot/bzImage', '/boot/bzImage' + self.kernelName[operator.indexOf(self.kernelName, '-'):])

				self.kernelImage = "bzImage" + self.kernelName[operator.indexOf(self.kernelName, '-'):]
			elif self.archName == "sparc64":
				shutil.copy('arch/' + self.archName + '/boot/image', '/boot/image' + self.kernelName[operator.indexOf(self.kernelName, '-'):])

				self.kernelImage = "image" + self.kernelName[operator.indexOf(self.kernelName, '-'):]
			elif self.archName == "x86_64":
				shutil.copy('arch/' + self.archName + '/boot/bzImage','/boot/bzImage' + self.kernelName[operator.indexOf(self.kernelName, '-'):])

				self.kernelImage = "bzImage" + self.kernelName[operator.indexOf(self.kernelName, '-'):]
			elif version == "2.4":
				if self.archName == "sparc32":
					shutil.copy('vmlinux', '/boot/vmlinux' + self.kernelName[operator.indexOf(self.kernelName, '-'):])

					self.kernelImage = "vmlinux" + self.kernelName[operator.indexOf(self.kernelName, '-'):]
			elif version == "2.6":
				if self.archName == "sparc32":
					shutil.copy('arch/sparc/boot/image', '/boot/image' + self.kernelName[operator.indexOf(self.kernelName, '-'):])

					self.kernelImage = "image" + self.kernelName[operator.indexOf(self.kernelName, '-'):]

			shutil.copy('.config', '/boot/config' + self.kernelName[operator.indexOf(self.kernelName, '-'):])
			shutil.copy('System.map', '/boot/System.map' + self.kernelName[operator.indexOf(self.kernelName, '-'):])
			os.remove('/boot/System.map')
			os.symlink('/boot/System.map' + self.kernelName[operator.indexOf(self.kernelName, '-'):], '/boot/System.map')

		else:
			os.system('mount /boot')
			self.install()
			shutil.copy('System.map', '/System.map')
			os.system('umount /boot')
		return
