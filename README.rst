Description
===========

Gentoo kernel updater.

This package provides a utility for automatically updating kernels (from 
various sources) on Gentoo systems.

Installation
============

This package is available through my overlay using the following method::

    layman -f -o http://www.alunduil.com/svn/portage/trunk/alunduil-overlay.xml -a alunduil-overlay
    emerge upkern

The latest release avilable is:

.. image:: https://badge.fury.io/py/upkern.png
    :target: http://badge.fury.io/py/upkern

If you prefer to clone this package directly from git or assist with 
development, the URL is https://github.com/alunduil/upkern and the current
status of the build is:

.. image:: https://secure.travis-ci.org/alunduil/upkern.png?branch=master
    :target: http://travis-ci.org/alunduil/upkern

Usage
=====

The simplest invocation of upkern, `upkern`, drops you into `menuconfig` for 
the latest kernel on the system.  The various options that upkern respects allow
this process to be personalized for the particular task at hand.  For more
information, see `upkern --help`.

Authors
=======

* Alex Brandt <alunduil@alunduil.com>

Known Issues
============

Known issues can be found in the github issue list at
https://github.com/alunduil/upkern/issues.

Troubleshooting
===============

If you need to troubleshoot an issue or submit information in a bug report, we
recommend obtaining the following pieces of information:

* output with the debug logging turned on (`--level debug` or `-l debug`)
* any relevant stack traces
