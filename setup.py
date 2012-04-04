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

from doc.man import build_manpage

setup_params = {}
setup_params['name'] = "upkern"
setup_params['version'] = "4.0.0"
setup_params['description'] = "Automated kernel updater for Gentoo."
setup_params["long_description"] = [
        "Defaults to building the most up to date kernel currently on the ",
        "system but can be used to build an alternative kernel by specifying ",
        "a name.  That name is an ebuild name for a kernel that at the very ",
        "least specifies a version (in which case the gentoo-sources will be ",
        "used).  Example names: 'sys-kernel/gentoo-sources-2.6.32-r6', ",
        "'gentoo-sources-2.6.23-r6', '2.6.33-r6', 'vanilla-sources-2.6.33'.  ",
        "The name passed must be the name of a current ebuild in the portage ",
        "tree.",
        ]
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
        "upkern.bootloader.bootloaders",
        "upkern.system",
        ]
setup_params['data_files'] = [
        ("share/doc/%s-%s" % (setup_params['name'], setup_params['version']), [
            "COPYING",
            "README",
            ]),
        ("share/man/man1", [
            "doc/man/man8/upkern.8",
            ]),
        ]
setup_params['requires'] = [
        "gentoolkit",
        "portage",
        ]
setup_params['cmdclass'] = {
        "build_manpage": build_manpage,
        }

setup(**setup_params)

