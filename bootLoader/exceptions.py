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

class BootLoaderError:

	# BootLoaderError Configurator ============================================
	# Function:         What the hell do you boot with?
	# PreConditions:    We can't find the bootloader.
	# PostConditions:   User knows that they don't have a bootloader.
	# Returns:          Exception.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# BootLoaderError round trip string =======================================
	# Function:         Let the programmer be mean so I don't have to.
	# PreConditions:    Programmer wants to forego my friendly message.
	# PostConditions:   User better install a bootloader.
	# Returns:          A string.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# BootLoaderError string ==================================================
	# Function:         Tell the user their home brewed bootloader is weird.
	# PreConditions:    The user must know this immediately, their bootloader
	#                   is missing.
	# PostConditions:   User better get their bootloader recognized.
	# Returns:          SSStttrrriiinnnggg.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The bootloader could not be determined.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

class BootNotFoundError:

	# BootNotFoundError Constructor ===========================================
	# Function:         Constructor of the 'your fstab blows' error.
	# PreConditions:    No errors.
	# PostConditions:   There is a typo in your fstab, my program cannot be
	#                   wrong in any way. It is omniscient too, so this error is
	#                   bogus.
	# Returns:          Laughing at you on the inside.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# BootNotFoundError round trip string =====================================
	# Function:         For the debugging, and possible resolution of an error.
	# PreConditions:    You screwed up that fstab file of yours.
	# PostConditions:   You are going to fix that fstab file of yours.
	# Returns:          A string that can be parsed.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# BootNotFoundError string return =========================================
	# Function:         Create a string that the user might like to see.
	# PreConditions:    Should we tell them?
	# PostConditions:   Hope that message wasn't too hurtful.
	# Returns:          An error string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The boot device could not be determined from your fstab.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

class FstabReadError:

	# FstabReadError Constructor ==============================================
	# Function:         Constructor of the 'where's your fstab?' error.
	# PreConditions:    No errors.
	# PostConditions:   Searching the system for your filesystem, and wondering
	#                   how you boot in the morning.
	# Returns:          Crying for your dearly departed hard drive
	#                   organization.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# FstabReadError round trip string ========================================
	# Function:         For the debugging, and possible resolution of an error.
	# PreConditions:    You screwed with that fstab file of yours.
	# PostConditions:   You are going to find that fstab file of yours.
	# Returns:          A string that can be parsed.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# FstabReadError string return ============================================
	# Function:         Create a string that informs the user to inform the
	#                   sysadmin about this problem...wait...isn't the user the
	#                   admin?
	# PreConditions:    Should we tell them? It might be fun to just tell them
	#                   to reboot the computer.
	# PostConditions:   The system still runs, unless something dumb happened.
	# Returns:          An error string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "There was a read error on /etc/fstab.\nIf this is a bug please file a bug report with Gentoo's bugzilla."
