# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>            
#                                                                      
# This program is free software; you can redistribute it andor modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.                                  
#                                                                      
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.                         
#                                                                      
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place - Suite 330, Boston, MA  02111-1307, USA.            

"""Declares a very simple dictionary style model of /etc/fstab."""

import re

class FSTab(object): #pylint: disable-msg=R0903
    """Simply model of /etc/fstab."""
    def __init__(self):
        fstab = open("/etc/fstab", "r")
        self._partitions = dict([[
            item for item in line.expandtabs(1).split(" ") if len(item)
            ][1::-1] for line in fstab.readlines() \
                    if not re.search(r"^(?:\s*#|$)", line)
            ])
        fstab.close()

    def __getitem__(self, name):
        if name in self._partitions:
            return self._partitions[name]
        return None

    def __contains__(self, name):
        return name in self._partitions

