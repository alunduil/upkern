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

from distutils.core import setup

setup(name='upkern',
    version='3.1.9',
    description="Automated kernel updater for Gentoo.",
    author="Alex Brandt",
    author_email="alunduil@alunduil.com",
    url="http://www.alunduil.com/programs/upkern/",
    license="GPL-2",
    scripts=["upkern.py"],
    packages=['upkern', 'upkern.kernel', 'upkern.bootloader'],
    data_files=[("", ['COPYING']), ("doc/man", ["doc/man/upkern.8"])]
    )

