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

class RootNotFoundError:

	# RootNotFoundError Constructor ===========================================
	# Function:         Constructor of the 'your fstab blows' error.
	# PreConditions:    No errors.
	# PostConditions:   There is a typo in your fstab, my program cannot be
	#                   wrong in any way. It is omniscient too, so this error is
	#                   bogus.
	# Returns:          Laughing at you on the inside.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# RootNotFoundError round trip string =====================================
	# Function:         For the debugging, and possible resolution of an error.
	# PreConditions:    You screwed up that fstab file of yours.
	# PostConditions:   You are going to fix that fstab file of yours.
	# Returns:          A string that can be parsed.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# RootNotFoundError string return =========================================
	# Function:         Create a string that the user might like to see.
	# PreConditions:    Should we tell them?
	# PostConditions:   Hope that message wasn't too hurtful.
	# Returns:          An error string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The root device could not be determined from your fstab.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

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

class BadKernelError:

	# BadKernelError Constructor ==============================================
	# Function:         Construct the proper message for our user to inform
	#                   them that they need to pass an argument in a slightly
	#                   specific way. In a way that doesn't take forever to
	#                   parse.
	# PreConditions:    User failed to read my mind...
	# PostConditions:   The user is informed of my needs, and can now
	#                   successfully read my mind in the future.
	# Returns:          A brand new error.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# BadKernelError round trip string ========================================
	# Function:         Pass back a parseable string for backticked messages.
	# PreConditions:    Did the user raise this exception?
	# PostConditions:   The programmer has a string which he can mangle before
	#                   telling the user what really happened.
	# Returns:          The telephony string.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# BadKernelError string return ============================================
	# Function:         Return my true intent to the user. (Boy I hope this
	#                   gets used.)
	# PreConditions:    The programmer decides this error is worth reporting my
	#                   way.
	# PostConditions:   I have voiced my opinion on the subject. What are we
	#                   talking about?
	# Returns:          A string? Of course, a string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "When passing a kernel to upkern it needs to be in one of two forms:\n\n\t[<sources>-]<version>[-r<revision>]\nor\n\t<version>[-<sources>][-r<revision>]\n"

class KernelNotFoundError:

	# KernelNotFoundError Constructor =========================================
	# Function:         Handle the situations where we get a kernel that
	#                   shouldn't be allowed. This could be due to many
	#                   reasons, but most commonly becuase of a masked kernel.
	# PreConditions:    User picked a bad kernel to try and update to.
	# PostConditions:   The user will not pick a better choice for a kernel.
	# Returns:          A brand new error.
	# -------------------------------------------------------------------------

	def __init__(self, kernelName):
		self.kernelName = kernelName

	# KernelNotFoundError round trip string ===================================
	# Function:         Pass back a parseable string so we can possibly state
	#                   what exactly cause the kernel to not be found.
	# PreConditions:    The kernel requested is not in portage.
	# PostConditions:   Don't expect the kernel to be in portage that's for
	#                   sure.
	# Returns:          The telephony string.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.kernelName

	# KernelNotFoundError string return =======================================
	# Function:         Tell the user that they have picked something bogus.
	# PreConditions:    The kernel is not in portage, and therefore can't be
	#                   anywhere.
	# PostConditions:   I'm going to sit here, and wait for that kernel to get
	#                   in portage. I think you should too.
	# Returns:          A string? Of course, a string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "There is no kernel '" + self.kernelName + "' in portage.\nIf this is incorrect check the http://packages.gentoo.org/packages/?category=sys-kernel; if it's a bug please file a bug report with Gentoo's bugzilla."

class KernelMaskedError:

	# KernelMaskedError Constructor ===========================================
	# Function:         What if the kernel is masked then what wise guy?
	# PreConditions:    Portage challenged me, and I accepted.
	# PostConditions:   Yell at the user for requesting the latest greatest
	#                   kernel.
	# Returns:          MASKED!
	# -------------------------------------------------------------------------

	def __init__(self, kernelName, maskWord):
		self.maskWord = maskWord
		self.kernelName = kernelName

	# KernelMaskedError round trip string =====================================
	# Function:         Pass back the keyword associated with the error.
	# PreConditions:    The kernel requested should not be requested by the
	#                   user, but it's their machine.
	# PostConditions:   Ask them if they want to live dangerously.
	# Returns:          A usable string.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return (self.kernelName, self.maskWord)

	# KernelMaskedError string return =========================================
	# Function:         Tell the user that their beloved kernel is masked.
	# PreConditions:    The requested kernel is just outside reach.
	# PostConditions:   Ask the user they know best.
	# Returns:          A string? A damn good string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The kernel '" + self.kernelName + "' is in portage, but is masked by the " + self.maskWord + " keyword.\nIf this is incorrect check the http://packages.gentoo.org/packages/?category=sys-kernel; if it's a bug please file a bug report with Gentoo's bugzilla."

class BadConfiguratorError:

	# BadConfiguratorError Constructor ========================================
	# Function:         Initialize one more error thingy.
	# PreConditions:    Did we get a good configurator?
	# PostConditions:   Tell the user what they can do now.
	# Returns:          A description of the different configuratiors.
	# -------------------------------------------------------------------------

	def __init__(self, configurator):
		self.configurator = configurator

	# BadConfiguratorError round trip string ==================================
	# Function:         Create a parseable string for the programmer.
	# PreConditions:    The programmer needs us, let's do a good job now.
	# PostConditions:   The programmer informs the user.
	# Returns:          The configurator the user thought they could use.
	# -------------------------------------------------------------------------

	def __repr__(self, configurator):
		return self.configurator

	# BadConfiguratorError string =============================================
	# Function:         Create a good list of the configurators.
	# PreConditions:    Does the user need to know this info?
	# PostConditions:   Let the user have it.
	# Returns:          A stringy string to string my string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return 'Configuration commands are:\n\nmenuconfig\t:: Text based color menus, radiolists & dialogs.\n\nxconfig\t\t:: X windows (Qt) based configuration tool.\n\ngconfig\t\t:: X windows (Gtk) based configuration tool.\n\noldconfig\t:: Default all questions based on the contents of your existing ./.config file and asking about new config symbols.\n\nsilentoldconfig\t:: Like above, but avoids cluttering the screen with questions already answered.\n\ndefconfig\t:: Create a ./.config file by using the default symbol values from arch/$ARCH/defconfig.\n\nallyesconfig\t:: Create a ./.config file by setting symbol values to "y" as much as possible.\n\nallmodconfig\t:: Create a ./.config file by setting symbol values to "m" as much as possible.\n\nallnoconfig\t:: Create a ./.config file by setting symbol values to "n" as much as possible.\n\nrandconfig\t:: Create a ./.config file by setting symbol values to random values.\n'

class SourceAccessDeniedError:

	# SourceAccessDeniedError Constructor =====================================
	# Function:         Create a message about file structure access.
	# PreConditions:    You can't enter your own directories.
	# PostConditions:   You are told about the situation.
	# Returns:          ERROR, ERROR
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# SourceAccessDeniedError round trip string ===============================
	# Function:         Return an informative string...
	# PreConditions:    Programmer what is your desire?
	# PostConditions:   Programmer what is your need?
	# Returns:          A string representation of itself.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# SourceAccessDeniedError string ==========================================
	# Function:         Tell me what's going on right now.
	# PreConditions:    The /usr/src/linux is borked?
	# PostConditions:   What are you going to do to fix this?
	# Returns:          A string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "Could not change directory into /usr/src/linux.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

class BadSourceTypeError:

	# BadSourceTypeError Constructor ==========================================
	# Function:         Create a prompt that the user doesn't know what sources
	#                   go on their own machine.
	# PreConditions:    The user is making a crazy request.
	# PostConditions:   Treat the user with caution they may be unstable.
	# Returns:          A nicely written error that they just need to think a
	#                   little.
	# -------------------------------------------------------------------------

	def __init__(self, sourceType):
		self.sourceType = sourceType

	# BadSourceTypeError round trip string ====================================
	# Function:         Pass the sources back to the author.
	# PreConditions:    The author wants to know what source has been denied.
	# PostConditions:   The author is in the know.
	# Returns:          The sourceType in fault.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.sourceType

	# BadSourceTypeError string ===============================================
	# Function:         Pass back a nice message.
	# PreConditions:    The user requested an invalid sourceType.
	# PostConditions:   The user has been informed, hopefully he hasn't thrown
	#                   a fit.
	# Returns:          A string.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The sources '" + self.sourceType + "' is not available for your architecture.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

class BogusSourceTypeError:

	# BogusSourceTypeError Constructor ========================================
	# Function:         Create an error that tells the user they are a liar.
	# PreConditions:    The user lies to the program.
	# PostConditions:   The user is scolded.
	# Returns:          The slap on the wrist.
	# -------------------------------------------------------------------------

	def __init__(self, sourceType):
		self.sourceType = sourceType

	# BogusSourceTypeError round trip string ==================================
	# Function:         Return a superior string to the superior user.
	# PreConditions:    User likes cats?
	# PostConditions:   User is informed that cats don't go into computers.
	# Returns:          A small punishment.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.sourceType

	# BogusSourceTypeError string =============================================
	# Function:         Returns an error message that the user better see.
	# PreConditions:    User make bad request.
	# PostConditions:   User's request must be denied.
	# Returns:          A string to be strung.
	# -------------------------------------------------------------------------

	def __str__(self):
		return "The sources '" + self.sourceType + "' is not valid.\nIf this is a bug please file a bug report with Gentoo's bugzilla."

class NoMakeOptError:

	# NoMakeOptError Constructor ==============================================
	# Function:			Create an error that tells the user they are stranger
	# 					than debian users. No makeopt, no build for you!
	# PreConditions:	The user doesn't want to take advantage of multiple
	# 					builds.
	# PostConditions:	User is informed of their strangeness.
	# Returns:			The scowl of discomfort.
	# -------------------------------------------------------------------------

	def __init__(self):
		return

	# NoMakeOptError Round Trip String ========================================
	# Function:			Return the error message because there is only one way
	# 					to yell at negligent people.
	# PreConditions:	The user is lethargic, or not a Gentoo user.
	# PostConditions:	The user is informed of their lazy or non-Gentoo ways.
	# Returns:			Super String for the string needs of the super user.
	# -------------------------------------------------------------------------

	def __repr__(self):
		return self.__str__()

	# NoMakeOptError String ===================================================
	# Function:			Return the error message, because this message is high
	# 					priority.
	# PreConditions:	The user gets smacked around for their negligence.
	# PostConditions:	Call the medic.
	# Returns:			The news flash for the user.
	# -------------------------------------------------------------------------

	def __str__(self):
		return 'The number of parallel builds you would like was not able to be determined from your /etc/make.conf. Please, check that you have the appropriate line, MAKEOPTS="-jN".'
