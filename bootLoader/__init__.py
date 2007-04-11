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

import re
import os
from string import ascii_lowercase
import datetime
import operator
import shutil

## BootLoader Class Definition:

class BootLoader:

	# BootLoader class constructor ============================================
	# Function:         Construct a new BootLoader config file, and install it.
	# PreConditions:
	# PostConditions:   The system is ready for a reboot into the new kernel.
	# Returns:          BootLoader configuration.
	# -------------------------------------------------------------------------

	def __init__(self, kernelName, rootPartition, isBootMounted = False, splashTheme = "", initrd = "", kernelOptions = ""):

		self.rootPartition = rootPartition
		self.isBootMounted = isBootMounted
		self.kernelName = kernelName
		self.splashTheme = splashTheme
		self.initrd = initrd
		self.kernelOptions = kernelOptions

		self.setBootLoader()

		self.setBoot()

		if self.bootLoader == "grub":
			self.setGrubRoot()
		elif self.bootLoader == "silo":
			self.setSiloNumber()

		if not self.hasKernel():
			self.setKernelString()

	# BootLoader class round trip string ======================================
	# Function:         Create a string that is returned to the programmer.
	# PreConditions:
	# PostConditions:
	# Returns:          A string that identifies the object.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.bootLoader

	# BootLoader class string =================================================
	# Function:         Create a string returnable for the user to view.
	# PreConditions:
	# PostConditions:
	# Returns:          A string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return self.bootLoader

	# setBootLoader() =========================================================
	# Function:         Set the boot loader the system uses.
	# PreConditions:
	# PostConditions:   We know what you boot with.
	# Returns:          The objects defining characteristic.
	# -------------------------------------------------------------------------

	def setBootLoader(self):

		bootLoaderExpression = re.compile('^\[ebuild\s+R\s+\].+$')

		grubOutput = os.popen('emerge -p grub 2>/dev/null | tail -n1', 'r')
		liloOutput = os.popen('emerge -p lilo 2>/dev/null | tail -n1', 'r')
		siloOutput = os.popen('emerge -p silo 2>/dev/null | tail -n1', 'r')

		grubMatch = bootLoaderExpression.match(grubOutput.readline())
		liloMatch = bootLoaderExpression.match(liloOutput.readline())
		siloMatch = bootLoaderExpression.match(siloOutput.readline())

		if liloMatch:
			self.bootLoader = "lilo"
			self.configLocation = "/etc/lilo.conf"
		elif grubMatch:
			self.bootLoader = "grub"
			self.configLocation = "/boot/grub/menu.lst"
		elif siloMatch:
			self.bootLoader = "silo"
			self.configLocation = "/etc/silo.conf"
		else:
			raise exceptions.BootLoaderError

	# setBoot() ===============================================================
	# Function:         Get the boot partition's information.
	# PreConditions:
	# PostConditions:   We know where you are boot partition.
	# Returns:          Information, I need more information.
	# -------------------------------------------------------------------------

	def setBoot(self):

		bootExpression = re.compile('^(/dev/(?P<device>\w+))\s+/boot\s+.+$', re.IGNORECASE)

		if os.access('/etc/fstab', os.F_OK):
			fstab = open('/etc/fstab', 'r')
			for line in fstab:
				if bootExpression.match(line):
					self.bootPartition = bootExpression.match(line).group("device")
					break
			else:
				if self.isBootMounted:
					self.bootPartition = self.rootPartition
				else:
					raise exceptions.BootNotFoundError
		else:
			raise exceptions.FstabReadError

	# setGrubRoot() ===========================================================
	# Function:         Get the root partition for the grub configuration file.
	# PreConditions:    We have to know the root partition.
	# PostConditions:   We have the name of the grub's root.
	# Returns:          Root device for grub configuration.
	# -------------------------------------------------------------------------

	def setGrubRoot(self):

		partOne = ascii_lowercase.find(self.bootPartition[2])
		partTwo = str(int(self.bootPartition[3]) - 1)

		self.grubRoot = "(hd" + `partOne` + "," + `partTwo` + ")"

	# hasKernel() =============================================================
	# Functions:        Check if the kernel we want to add is already in the
	#                   configuration file.
	# PreConditions:    The boot loader has been successfully determined.
	# PostConditions:
	# Returns:          True or False, I wonder how that is determined. True
	#                   for kernel in configuration file, and False for kernel
	#                   not in configuration file.
	# -------------------------------------------------------------------------

	def hasKernel(self):
		if self.isBootMounted:
			if self.bootLoader == "grub":

				kernelExpression = re.compile('$.+kernel\s+/boot/' + self.kernelName + '\s+.+$')

			elif self.bootLoader == "lilo":

				kernelExpression = re.compile('$image=/boot/' + self.kernelName + '.+$')

			elif self.bootLoader == "silo":

				kernelExpression = re.compile('$image\s=\s/boot/' + self.kernelName + '.+$')

			if os.access(self.configLocation, os.F_OK):
				menuFile = open(self.configLocation, 'r')
			else:
				raise MenuReadError
			for line in menuFile:
				if kernelExpression.match(line):
					menuFile.close()
					return True
			else:
				menuFile.close()
				return False
		else:
			os.system('mount /boot')
			self.hasKernel()
			os.system('mount /boot')

	# setKernelString() =======================================================
	# Function:         Add a kernel to the menu for the loader.
	# PreConditions:    We know what we are putting were.
	# PostConditions:   We have the string prepared to place in our file.
	# Returns:          The kernel string to place in the file.
	# -------------------------------------------------------------------------

	def setKernelString(self):

		self.kernelString = "\n# Kernel added by upkern on " + `datetime.date.today()` + "\n"

		if self.bootLoader == "grub":

			self.kernelString + "title=" + self.kernelName + "\n\troot " + self.rootPartition + "\n\tkernel " + self.kernelName[operator.indexOf('-', self.kernelName):] + " root=" + self.rootPartition

			if len(self.kernelOptions) != 0:
				self.kernelString += " " + self.kernelOptions
			if len(self.splashTheme) != 0:
				self.kernelString += " " + self.splashTheme.getBootLoaderString()
			if len(self.initrd) != 0:
				self.kernelString += "\n\tinitrd " + self.initrd
		elif self.bootLoader == "lilo":
			self.kernelString += "image=/boot/" + self.kernelName + "\n\tlabel=" + self.kernelName + "\n\troot=" + self.rootPartition + "\n\tread-only"
			if len(self.kernelOptions) != 0:
				self.kernelString += "\n\tappend=" + self.kernelOptions
			if len(self.initrd) != 0:
				self.kernelString += "\n\tinitrd=" + self.initrd
		elif self.bootLoader == "silo":
			self.kernelString += "\image=/boot/" + self.kernelName + "\n\tlabel=" + self.kernelName

	# createConfiguration() ===================================================
	# Function:         Create a temporary file that houses our configuration.
	# PreConditions:
	# PostConditions:   A temp file, bootLoader.temp, is created, and is ready
	#                   to be installed as the working configuration.
	# Returns:
	# -------------------------------------------------------------------------

	def createConfiguration(self):

		if self.isBootMounted:
			grubExpression = re.compile('^(default\s+)(?P<kernelNumber>\d+)$')
			liloExpression = re.compile('^(default=)(?P<defaultEntry>.+)$')
			siloExpression = re.compile('^(default\s=\s)(?P<defaultEntry>.+)$')

			if os.access(self.configLocation, os.F_OK):
				menuFile = open(self.configLocation, 'r')
				newMenuFile = open(self.configLocation + '.tmp', 'w')

				for line in menuFile:
					match = grubExpression.match(line) or liloExpression.match(line) or siloExpression.match(line)

					if match and not self.hasKernel():
						if self.bootLoader == "grub":
							newMenuFile.write(match.group(1) + string(int(match.group("kernelNumber")) + 1))
						elif self.bootLoader == "lilo" or self.bootLoader == "silo":
							newMenuFile.write(match.group(1) + self.kernelName)
					else:
						newMenuFile.write(line)
				newMenuFile.write(self.kernelString)

				menuFile.close()
				newMenuFile.close()
		else:
			os.system('mount /boot')
			self.createConfiguration()
			os.system('umount /boot')

	# installConfiguration() ==================================================
	# Function:         Install the temporary file into its permanent home.
	# PreConditions:    The temporary file has been created.
	# PostConditions:   The temporary file is moved into the permanent home.
	# Returns:
	# -------------------------------------------------------------------------

	def installConfiguration(self):
		if self.isBootMounted:
			if os.access(self.configuration + '.tmp', os.F_OK):
				shutil.move(self.configuration + '.tmp', self.configuration)
		else:
			os.system('mount /boot')
			self.installConfiguration()
			os.system('umount /boot')
