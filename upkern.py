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

import sys

from upkern import Upkern, Output

def main(args):
    try:
        Output.debug(__file__, __line__, "args", args)
        application = Upkern(args)
        application.Run()
    except UpkernArgumentException, e:
        if (len(e.GetMessage()) > 0):
            Output.error(e.GetMessage())
        Output.error(e.GetDescription())
        return 1
    except UpkernException, e:
        if (len(e.GetMessage()) > 0):
            Output.error(e.GetMessage())
        return 1
    return 0

