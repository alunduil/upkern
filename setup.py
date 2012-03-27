#!/usr/bin/env python -t3
# -*- coding: utf-8 -*-

# Copyright (C) 2011 by Alex Brandt <alunduil@alunduil.com>
#
# This program is free software; you can redistribute it and#or modify it under
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

from distutils.core import setup

setup_params = {}
setup_params['name'] = "upkern"
setup_params['version'] = "3.2.0"
setup_params['description'] = "Automated kernel updater for Gentoo."
setup_params['author'] = "Alex Brandt"
setup_params['author_email'] = "alunduil@alunduil.com"
setup_params['url'] = "http://www.alunduil.com/programs/upkern/"
setup_params['license'] = "GPL-2"
setup_params['scripts'] = [
        "bin/upkern",
        ]
setup_params['packages'] = [
        "upkern",
        "upkern.kernel",
        "upkern.bootloader",
        ]
setup_params['data_files'] = [
        ("share/doc/%s%s" % (setup_params['name'], setup_params['version']), [
            "COPYING",
            "README",
            ]),
        ("share/man/man1", [
            "doc/man/man1/upkern.1",
            ]),
        ]
setup_params['requires'] = [
        "gentoolkit",
        "portage",
        ]

setup(**setup_params)

