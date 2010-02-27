# -*- coding: utf-8 -*-

########################################################################
# Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>            #
#                                                                      #
# This program is free software; you can redistribute it and#or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 2 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with this program; if not, write to the                        #
# Free Software Foundation, Inc.,                                      #
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.            #
########################################################################

from upkern import Kernel, KernelException

import unittest

class KernelTest(unittest.TestCase):
    def setUp(self):
        self.kernelA = Kernel("menuconfig", "", True, "", False, True, True, True)
        self.kernelB = Kernel("oldconfig", "gentoo-sources-2.6.32-r6", True, "", False, True, True, True)

    def tearDown(self):
        pass

    def testInitWithoutSources(self):
        try:
            Kernel("menuconfig", "git-sources-2.6.33", True, "", False, True, True, True)
        except KernelException:
            self.assertTrue(True, "did not error when sources were not found")

    def testInitWithNoSpecifiedSources(self):
        try:
            Kernel("menuconfig", "", True, "", False, True, True, True)
        except KernelException:
            self.assertTrue(False, "errored when sources weren't specified")

    def testInitWithSpecifiedSources(self):
        try:
            Kernel("oldconfig", "gentoo-sources-2.6.32-r6", True, "", True, True, True, True)
        except KernelException:
            self.assertTrue(False, "errored when sources were specified and found")

    def testGetName(self):
        # This is system specific and should be changed for the system
        # being run on.
        self.assertEqual(self.kernelA.get_name(), "linux-2.6.33-gentoo", "incorrect directory")
        self.assertEqual(self.kernelB.get_name(), "linux-2.6.33-gentoo", "incorrect direcotry")
        self.assertEqual(self.kernelC.get_name(), "linux-2.6.32-gentoo-r6", "incorrect directory")

    def testGetImage(self):
        import platform
        if platform.machine() == "x86_64":
            self.assertEqual(self.kernelA.get_image(), "bzImage", "incorrect image")

    def testGetSuffix(self):
        # This is system specific and should be changed for the system
        # being run on.
        self.assertEqual(self.kernelA.get_suffix(), "-2.6.33-gentoo", "incorrect suffix")
        self.assertEqual(self.kernelB.get_suffix(), "-2.6.32-gentoo-r6", "incorrect suffix")

    # Unfortunately a lot of this class is not obviously unit testable.

    def testHaveModuleRebuild(self):
        # This is system specific and should be changed for the system
        # being run on.
        self.assertEqual(self.kernel._have_module_rebuild(), True, "incorrect determination of rebuild-modules")

    def testGetInstallImage(self):
        import platform
        if platform.machine() == "x86_64" or platform.machine() == "i686":
            self.assertEqual(self.kernelA._get_install_image(), "bzImage", "incorrect image")

    def testGetKernelNames(self):
        self.assertEqual(self.kernelA._get_kernel_name("2.6.33"), ("linux-2.6.33-gentoo", "sys-kernel/gentoo-sources-2.6.33"), "incorrect directory name or package name")

    def testGetKernelDirectories(self):
        # Again, system specific.  These need to be written in a more
        # agnostic fashion.
        directory_list = [
            ""
            ]
        self.assertEqual(self.kernelA._get_kernel_directories(), directory_list, "incorrect directory listing")

