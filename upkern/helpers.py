# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging

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
        logger.error('emerge requires root permissions')

        sys.exit(1)
    else:
        status = subprocess.call(command, shell = True)

        if status != 0:
            pass # TODO raise an appropriate exception

def mountedboot(func):
    """A decorator that checks if boot is mounted before running the function.

    If boot is not mounted; it gets mounted and unmounted properly.

    """

    def new_func(*args, **kargs):
        """Closure definition."""
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
            try:
                res = func(*args, **kargs)
            except:
                raise
            finally:
                os.system('umount /boot')
        return res
    return new_func

