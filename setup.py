############################################################################
#    Copyright (C) 2008 by Alex Brandt <alunduil@alunduil.com>   #
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

from distutils.core import setup

setup(
    name='upkern',
    version='2.0.11',
    description="Automated Gentoo kernel updater.",
    license="GPL-2",
    author="Alex Brandt",
    author_email="alunduil@alunduil.com",
    url="http://www.alunduil.com/programs/python-kernel-updater",
    scripts=["upkern.py"],
    py_modules=['upkern', 'kernel', 'bootloader', 'upkern_helpers']
    )
