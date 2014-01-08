# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import importlib
import itertools
import logging
import os

logger = logging.getLogger(__name__)

def emerge(package, options = None):
    '''Wrapper for portage's emerge functionality.

    This method is just a wrapper for de-coupling purposes.  The implementation
    is malleable and reusable.

    .. note::
        This causes a critical (application stopping) error if not run as root.

    '''

    command = 'emerge'

    if options is not None:
        command += ' ' + ' '.join(options)

    command += ' ' + package

    logger.debug('command: %s', command)

    if os.getuid() != 0:
        raise PermissionError('emerge requires root permissions')
    else:
        status = subprocess.call(command, shell = True)

        if status != 0:
            pass # TODO raise an appropriate exception

def mount(mountpoint):
    '''Mount the specified location unless it's already mounted.

    In the typical idempotent fashion, this mounts the specified location unless
    it's already mounted.

    .. note::
        This assumes the mountpoint is defined in `/etc/fstab` and if not found
        there, it will throw an error.

    Returns
    -------

    True if the location was mounted; otherwise, False.

    '''

    if os.path.ismount(mountpoint):
        return False

    command = 'mount {0}'.format(mountpoint)
    status = subprocess.call(command, shell = True)

    if status != 0:
        pass # TODO raise an appropriate exception

    return True

def unmount(mountpoint):
    '''Unmount the specified location.

    .. note::
        This unconditionally unmounts the specified mountpoint.

    '''

    command = 'umount {0}'.format(mountpoint)
    status = subprocess.call(command, shell = True)

    if status != 0:
        pass # TODO raise an appropriate exception

def load_all_modules(module_basename, directory, update_path = False):
    '''Load all modules in a given directory recursively.

    All python modules in the given directory will be imported.

    Parameters
    ----------

    :``module_basename``: Module name prefix for loaded modules.
    :``directory``:       Directory to recursively load python modules from.
    :``update_path``:     If True, the system path for modules is updated to
                          include ``directory``; otherwise, it is left alone.

    '''

    if update_path:
        update_path = bool(sys.path.count(directory))
        sys.path.append(directory)

    logger.info('loading submodules of %s', module_basename)
    directory = os.path.dirname(__file__)

    filenames = itertools.chain(*[ [ os.path.join(_[0], filename) for filename in _[2] ] for _ in os.walk(directory) if len(_[2]) ])

    module_names = []
    for filename in filenames:
        if filename.endswith('.py'):
            _ = filename

            _ = _.replace(directory + '/', '')
            _ = _.replace('__init__.py', '')
            _ = _.replace('.py', '')

            if len(_):
                module_names.append(module_basename + '.' + _)

    logger.debug('modules found: %s', list(module_names))

    for module_name in module_names:
        logger.info('loading module %s', module_name)

        try:
            importlib.import_module(module_name)
        except ImportError as e:
            logger.warning('failed loading %s', module_name)
            logger.exception(e)
        else:
            logger.info('successfully loaded %s', module_name)

    if update_path:
        sys.path.remove(directory)
