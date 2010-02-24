#!/usr/bin/env python -t3
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

from sys import stderr
from inspect import stack

class Colors:
    GRAY = "\033[22;37m"
    LIGHT_RED = "\033[01;31m"
    YELLOW = "\033[01;33m"
    LIGHT_BLUE = "\033[01;34m"
    LIGHT_GREEN = "\033[01;32m"

def debug(file, dict):
    # @todo Turn this into a formatted string.
    # @todo I think this is ugly and thus we should find a better way.
    output = Colors.YELLOW + file + ":" + str(stack()[1][2]) + \
        ": DEBUG:"
    extension_list = []
    for key, value in dict.iteritems():
        extension_list.extend([" ", str(key), '->', str(value)])
    output += " " + " ".join(extension_list[1:]) + Colors.GRAY
    print >> stderr, output

def error(msg, *args):
    output = Colors.LIGHT_RED + "ERROR: "
    if len(args) > 0: ouput += msg % args
    else: output += msg
    print >> stderr, output + Colors.GRAY

