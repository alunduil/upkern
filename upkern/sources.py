# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import gentoolkit.helpers
import gentoolkit.query
import logging
import os
import portage
import re
import shutil
import subprocess

from upkern import system

logger = logging.getLogger(__name__)

_kernel_index_expression = re.compile(
        r'.*?(?P<major>\d+)\.'
        r'(?P<minor>\d+)'
        r'(?:\.(?P<patch>\d+))?'
        r'-[^-]*(?:-r(?P<revision>\d+))?'
        )

def kernel_index(kernel_string):
    '''Map the kernel_string to an integer.

    The generated integer is always greater for a newer kernel version.

    Examples
    --------

    >>> kernel_index('linux-3.10.7-gentoo-r1')
    3010007001

    >>> kernel_index('linux-3.12.6-gentoo')
    3012006000

    '''

    logger.debug('kernel_string: %s', kernel_string)

    _ = _kernel_index_expression.match(kernel_string)

    major = minor = patch = revision = '0'
    if _:
        major, minor, patch, revision = _.groups('0')

    key = '{:03d}{:03d}{:03d}{:03d}'.format(int(major), int(minor), int(patch), int(revision))

    logger.debug('kernel_index: %s', key)

    return int(key)

class Sources(object):
    def __init__(self, name = None):
        self.name = name
        self.built = False

        self._packages = {}

    @property
    def configuration_files(self):
        '''List of configuration files present in `/boot`.

        .. note::
            This property will mount the /boot filesystem if possible.

        '''

        if not hasattr(self, '_configuration_files'):
            boot_mounted = system.utilities.mount('/boot')

            self._configuration_files = [ _ for _ in os.listdir('/boot') if re.match('config-.+', _) ]

            if boot_mounted:
                system.utilities.unmount('/boot')

            self._configuration_files = sorted(self._configuration_files, key = kernel_index, reverse = True)

        return self._configuration_files

    @property
    def directory_name(self):
        '''Name of the sources directory in `/usr/src/`.

        Provides the first directory in `/usr/src` that is a member of
        `self.package_name`.

        .. note::
            This property is cached after the first invocation until the object
            is garbage collected.

        '''

        if not hasattr(self, '_directory_name'):
            finder = gentoolkit.helpers.FileOwner()

            logger.debug('self.source_directories: %s', self.source_directories)

            for directory in self.source_directories:
                logger.info('finding the owner of %s', directory)

                package = self._packages.get(directory, str(finder(('/usr/src/' + directory, ))[0][0]))

                logger.debug('package: %s', package)

                logger.info('finished finding the owner of %s', directory)

                self._packages[directory] = package

                logger.debug('self.package_name: %s', self.package_name)

                if package == self.package_name.lstrip('='):
                    self._directory_name = directory

                    logger.info('using source directory: %s', self._directory_name)

                    break

        return self._directory_name

    @property
    def package_name(self):
        '''Name of the kernel sources package.

        Using the specified name, we determine which sources should be mapped
        by this object.

        If the name is not set, we use the most up to date source directory and
        use portage to determine the package name.

        .. note::
            This property is cached after the first invocation until the object
            is garbage collected.

        '''

        if not hasattr(self, '_package_name'):
            package_expression = re.compile(
                    r'(?:sys-kernel/)?' \
                    r'(?:(?P<sources>[A-Za-z0-9+_][A-Za-z0-9+ -]*)-sources-)?' \
                    r'(?P<version>[A-Za-z0-9+_][A-Za-z0-9+_.-]*)'
                    )

            if self.name is None:
                logger.info('using latest kernel sources')

                finder = gentoolkit.helpers.FileOwner()

                logger.info('finding the owner of %s', self.source_directories[0])

                package = '=' + self._packages.get(self.source_directories[0], str(finder(('/usr/src/' + self.source_directories[0], ))[0][0]))

                logger.debug('package: %s', package)

                logger.info('finished finding the owner of %s', self.source_directories[0])

                self._packages[self.source_directories[0]] = package

                self._package_name = package
            else:
                logger.info('parsing %s', self.name)

                self._package_name = '=sys-kernel/'

                package_match = package_expression.match(self.name)

                if package_match:
                    sources = 'gentoo'
                    if package_match.group('sources'):
                        sources = package_match.group('sources')

                    self._package_name += sources
                    self._package_name += '-sources-'
                    self._package_name += package_match.group('version')

        return self._package_name

    @property
    def portage_configuration(self):
        '''System's Portage configuration.

        Basically, a dictionary of `emerge -info` output.

        .. note::
            This property is cached after the first invocation until the object
            is garbage collected.

        '''

        if not hasattr(self, '_portage_configuration'):
            self._portage_configuration = portage.config()

        return self._portage_configuration

    @property
    def source_directories(self):
        '''List of source directories in `/usr/src`.

        Uses an integer mapping of kernel versions to determine the ordering
        for the directories in this list.  The ordering of the source
        directories will be most recent to least recent (by version number).

        .. note::
            This property is cached after the first invocation until the object
            is garbage collected.

        '''

        if not hasattr(self, '_source_directories'):
            directories = [ _ for _ in os.listdir('/usr/src') if re.match(r'linux-.+$', _) ]

            self._source_directories = sorted(directories, key = kernel_index, reverse = True)

        return self._source_directories

    def build(self):
        '''Build the kernel.

        1. Enter the source directory
        2. Run `make && make modules_install`
        3. Leave the source directory

        '''

        logger.info('building the kernel sources')

        original_directory = os.getcwd()

        make_options = self.portage_configuration['MAKEOPTS']
        if logger.level > 29:
            make_options += ' -s'

        command = 'make {0} && make {0} modules_install'.format(make_options)

        logger.debug('command: %s', command)

        os.chdir('/usr/src/linux')

        status = subprocess.call(command, shell = True)

        if status != 0:
            raise RuntimeError('kernel did not build correctly')

        os.chdir(original_directory)

        logger.info('finished building the kernel sources')

    def configure(self, configurator = 'menuconfig', accept_defaults = False):
        '''Configure the kernel sources.

        1. Enter the source directory.
        2. Run `make ${CONFIGURATOR}`
        3. Leave the source directory.

        '''

        logger.info('configuring kernel sources')

        original_directory = os.getcwd()

        command = 'make {0} {1}'.format(
                self.portage_configuration['MAKEOPTS'],
                configurator
                )

        if accept_defaults:
            command = 'yes "" | ' + command

        logger.debug('command: %s', command)

        os.chdir('/usr/src/linux')

        status = subprocess.call(command, shell = True)

        if status != 0:
            pass  # TODO raise an appropriate exception.

        os.chdir(original_directory)

        logger.info('finished configuring kernel sources')

    def emerge(self, force = False):
        '''Install the kernel sources.

        Use portage to install the kernel sources.

        '''

        logger.info('emerging kernel sources')

        _ = gentoolkit.query.Query(self.package_name).find_installed()
        logger.debug('installed: %s', _)

        logger.debug('force: %s', force)

        _ = not len(_) or force
        logger.debug('emerge? %s', _)

        if _:
            options = [ '-n', '-1' ]

            if logger.level < 30:
                options.append('-v')
            else:
                options.append('-q')

            system.portage.emerge(options = options, package = self.package_name)

        logger.info('finished emerging kernel sources')

    def prepare(self, configuration):
        '''Prep the sources so they are ready to be built.

        1. Setup the `/usr/src/linux` symlink
        2. Copy the current configuration file from `/boot`

        '''

        logger.info('preparing the kernel sources')

        self._setup_symlink()
        self._copy_configuration(configuration)

        logger.info('finished preparing the kernel sources')

    def _copy_configuration(self, configuration = None):
        '''Copy the configuration file into /usr/src/linux.

        .. note::
            This method leaves the environment in the state it found it even if
            any errors occur.

        '''

        logger.info('copying kernel configuration')

        if configuration is None:
            if len(self.configuration_files):
                configuration = os.path.join(os.path.sep, 'boot', self.configuration_files[0])
            else:
                logger.info('no eligible configuration files found')
                logger.info('aborting copying kernel configuration')
                return

        logger.info('using configuration: %s', configuration)

        try:
            if os.path.lexists('/usr/src/linux/.config'):
                shutil.move('/usr/src/linux/.config', '/usr/src/linux/.config.bak')
            shutil.copy(configuration, '/usr/src/linux/.config')
        except Exception as e:
            logger.exception(e)
            logger.error('failed to copy kernel configuration')
            logger.warn('please, submit a bug report including the previous traceback')

            if os.path.lexists('/usr/src/linux/.config.bak'):
                shutil.move('/usr/src/linux/.config.bak', '/usr/src/linux/.config')

            raise
        else:
            if os.path.lexists('/usr/src/linux/.config.bak'):
                os.remove('/usr/src/linux/.config.bak')

        logger.info('finished copying kernel configuration')

    def _setup_symlink(self):
        '''Create the `/usr/src/linux` symlink.

        .. note::
            This method leaves the environment in the state it found it even if
            any errors occur.

        '''

        logger.info('symlinking /usr/src/linux')

        original_target = None

        try:
            if os.path.islink('/usr/src/linux'):
                original_target = os.readlink('/usr/src/linux')
                os.remove('/usr/src/linux')
            os.symlink(self.directory_name, '/usr/src/linux')
        except Exception as e:
            logger.exception(e)
            logger.error('failed to symlink /usr/src/linux')
            logger.warn('please, submit a bug report including the previous traceback')

            if os.path.islink('/usr/src/linux'):
                os.remove('/usr/src/linux')

            if original_target is not None:
                os.symlink(original_target, '/usr/src/linux')

            raise

        logger.info('finished symlinking /usr/src/linux')
