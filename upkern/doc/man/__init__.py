# -*- coding: utf-8 -*-

# Copyright (C) 2012 by Alex Brandt <alunduil@alunduil.com>
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

"""The documentation module for building man pages.

This module is not intended to be nor is included in the final release.  It is
meant to be ran as part of the tarball generation (before is probably better)
and then the statically generated man page will be included in the sdist.

"""

import argparse
import datetime
import re

from distutils.command.build import build
from distutils.core import Command

from upkern.application import UpkernOptions

def _markup(txt):
    """Prepare passed text to be used in man pages."""

    return txt.replace('-', '\\-')

class ManPageFormatter(argparse.HelpFormatter):
    """A man page formatter for argparse.

    Unabashedly stolen from the wonderfully helpful site:
    http://andialbrecht.wordpress.com/2009/03/17/creating-a-man-page-with-distutils-and-optparse/

    """

    def __init__(self, indent_increment = 2, max_help_position = 24,
            width = None, short_first = 1):
        """Constructor

        optparse.HelpFormatter was not a new style class but let's find out
        about argparse.HelpFormatter.  Yes, I'm feeling lucky.

        """

        super(ManPageFormatter, self).__init__(indent_increment,
                max_help_position, width, short_first)

    def format_usage(self, usage):
        """Format the usage or synopsis line."""

        return _markup(usage)

    def format_heading(self, heading):
        """Format the passed heading.

        If we are at level zero we should return an empty string.  Usually this
        is the string "OPTIONS".

        """

        if self.level == 0:
            return ""
        return ".TP\n{0!s}\n".format(_markup(heading.upper()))

    def format_option(self, option):
        """Format a single option.

        The base class takes care to replace custom argparse values.

        """

        result = []

        opts = self.option_strings[option]
        result.append(".TP\n.B {0!s}\n".format(_markup(opts)))

        if option.help:
            help_text = "{0!s}\n".format(_markup(self.expand_default(option)))
            result.append(help_text)
        return "".join(result)

class build_manpage(Command):
    description = "Generate a man page."
    user_options = [
            ("output=", "o", "output file"),
            ]

    def initialize_options(self):
        self.output = None

    def finalize_options(self):
        if self.output is None:
            raise DistutilsOptionError("'output' option is required")

        self._parser = UpkernOptions("upkern").parser
        self._parser.formatter = ManPageFormatter()
        #self._parser.formatter.set_parser(self._parser)
        self.announce("Writing man page {0!s}".format(self.output))
        self._today = datetime.date.today()
    
    def run(self):
        manpage = []
        manpage.append(self._write_header())
        manpage.append(self._write_options())
        manpage.append(self._write_footer())
        stream = open(self.output, "w")
        stream.write("".join(manpage))
        stream.close()

    def _write_header(self):
        appname = self.distribution.get_name()

        ret = []
        ret.append(".TH {0!s} 8 {1!s} \"Linux System Administration\"\n".format(_markup(appname), self._today.strftime("%Y\\-%m\\-%d")))

        description = self.distribution.get_description()

        if description:
            name = _markup("{0!s} - {1!s}".format(_markup(appname), description.splitlines()[0]))
        else:
            name = _markup(appname)

        ret.append(".SH NAME\n{0!s}\n".format(name))

        synopsis = re.sub(r"\s+", " ", " ".join(self._parser.format_usage().split("\n"))).replace("usage: ", "")

        if synopsis:
            synopsis = synopsis.replace("{0!s} ".format(appname), "")
            ret.append(".SH SYNOPSIS\n.B {0!s}\n{1!s}\n".format(_markup(appname), synopsis))
        
        long_description = self.distribution.get_long_description()

        if long_description:
            ret.append(".SH DESCRIPTION\n{0!s}\n".format(_markup(long_description)))

        return "".join(ret)

    def _write_options(self):
        ret = []

        found = False

        options = self._parser.format_help().split('\n')

        opts = []

        for line in options:
            if not found:
                if line.startswith("optional arguments:"):
                    found = True
            else:
                opts.append(line)

        ret.append(".SH OPTIONS\n{0!s}\n".format(_markup("\n".join(opts))))

        return "".join(ret)

    def _write_footer(self):
        ret = []

        ret.append(".SH AUTHOR\n{0!s} <{1!s}>\n".format(_markup(self.distribution.get_author()), _markup(self.distribution.get_author_email())))

        ret.append(".SH \"SEE ALSO\"\n{0!s}\n".format(_markup(", ".join(sorted([".BR dracut(8)"])))))

        return "".join(ret)

build.sub_commands.append({"build_manpage", None})

