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

import os
import re
import itertools

def is_boot_mounted():
    """Determines if the system's boot partition is mounted.

    Just returns true if it finds a file in the /boot area, false 
    otherwise.

    """
    if os.path.ismount('/boot'): return True
    # Otherwise, we have more checking to do.
    files = [ f for f in list(itertools.chain(*[ [ os.path.join(x[0], fs) for fs in x[2] ] for x in os.walk("/boot") ] )) if not re.search("^/boot/(?:boot|.keep)", f) ]
    if len(files) > 0: return True
    return False
