# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>            
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

class Binary(object):
    """A kernel binary model.

    All references to how things should be called makes an attempt to coincide
    with the documentation provided in the relevant kernel sources.  If
    mismatches are discovered bugs should be reported to
    http://bugs.alunduil.com.  The reference sources will be those provided by
    the Gentoo Portage tree.

    See the following URL for a list of current kernel sources:
    http://packages.gentoo.org/packages/sys-kernel/gentoo-sources

    """

    def __init__(self, debug = False, verbose = False, quiet = False,
            dry_run = False): 
        """Returns a kernel binary object.

        Get the appropriate information about the system to know how to perform
        basic kernel actions.  Once the initial data discovery is complete
        (within this method), the normal sequence to build a kernel is the
        following:

        """

        self.arguments = {
                "debug": debug,
                "verbose": verbose,
                "quiet": quiet,
                "dry_run": dry_run,
                }

    @property
    def install_image(self):
        """Returns the name of the install image for this architecture.
        
        Return bzImage, vmlinux, etc depending on the arch of the machine.

        From the kernel README:
          
        Although originally developed first for 32-bit x86-based PCs (386 or
        higher), today Linux also runs on (at least) the Compaq Alpha AXP, Sun
        SPARC and UltraSPARC, Motorola 68000, PowerPC, PowerPC64, ARM, Hitachi
        SuperH, Cell, IBM S/390, MIPS, HP PA-RISC, Intel IA-64, DEC VAX, AMD
        x86-64, AXIS CRIS, Xtensa, AVR32 and Renesas M32R architectures.

        We will support more of these as we get accurate reports of what image
        is produced by the default make command.

        """

        if not hasattr(self, "_install_image"):
            self._install_image = {
                    "x86_64": "bzImage",
                    "i686": "bzImage",
                    }[platform.machine()]

        return self._install_image

