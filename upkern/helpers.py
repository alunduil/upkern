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

"""Upkern helper functions.

Simple things like printing common errors, verbose, and debugging output.

"""

__all__ = [
        "error",
        "debug",
        "verbose",
        ]

import sys
import os
import itertools

from inspect import stack

from upkern.colors import TerminalController

TERMINAL = TerminalController()

COLORIZE = "none"

def colorize(color, message, out = sys.stdout):
    """Colorize the given message with the given color.

    If COLOR is "none" we shall simply bypass colorizing otherwise we will try
    to add the requested appropriate color.

    """
    if COLORIZE == "none":
        print >> out, message
    else:
        print >> out, TERMINAL.render('${{{color}}}{message}${{NORMAL}}'.format(
            color = color, message = message))

def debug(file_, message = None, *args, **kwargs):
    """Print a debugging message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([ 
            "{key} -> {value}".format(key = key, value = val) for key, val in kwargs.items()
            ])

    for line in output:
        colorize("YELLOW", "D: {file_}:{function} {line}".format(file_ = file_,
            function = unicode(stack()[1][2]), line = line), sys.stderr)

def verbose(message = None, *args, **kwargs):
    """Print a verbose message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "{key} -> {value}".format(key = key, value = val) for key, val in kwargs.items()
            ])

    for line in output:
        colorize("BLUE", "V: {line}".format(line = line), sys.stderr)

def error(message = None, *args, **kwargs):
    """Print an error message to the standard error."""

    output = []

    if message and len(args):
        output.append(message.format(args))
    elif message:
        output.append(message)

    if len(kwargs.values()):
        output.extend([
            "{key} -> {value}".format(key = key, value = val) for key, val in kwargs.items()
            ])

    for line in output:
        colorize("RED", "E: {line}".format(line = line), sys.stderr)

def sufficient_privileges(short_circuit = False):
    """Return the truthness of the process being root."""
    return short_circuit or os.getuid() == 0

def mountedboot(func):
    def new_func(*args, **kargs):
        if os.path.ismount("/boot") or \
                len([
                    f for f in list(
                        itertools.chain(*[
                            [
                                os.path.join(x[0], fs) for fs in x[2]
                                ]
                            for x in os.walk("/boot")
                            ])
                        ) if not re.search("^/boot/(?:boot|.keep)", f)
                    ]):
            res = func(*args, **kargs)
        else:
            os.system('mount /boot')
            res = func(*args, **kargs)
            os.system('umount /boot')
        return res
    return new_func

