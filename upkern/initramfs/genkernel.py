# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

import logging
import subprocess

from upkern.initramfs import PREPARERS

logger = logging.getLogger(__name__)


class GenKernelPreparer(object):
    @property
    def options(self):
        '''List of options that will be passed to genkernel.


        .. note::
            This property is empty until configure sets the options.

        '''

        if not hasattr(self, '_options'):
            logger.warn('configure may not have been called yet')
            raise AttributeError('no options have been set')

        return self._options

    def build(self):
        '''Build the initramfs object.

        Invoke genkernel to build initramfs.

        '''

        logger.info('building the initramfs')

        command = 'genkernel --no-ramdisk-modules {0} initramfs'.format(self.options)
        command = ' '.join(command.split())

        logger.debug('command: %s', command)

        status = subprocess.call(command, shell = True)

        if status != 0:
            raise RuntimeError('initramfs did not build correctly')

        logger.info('finished building the initramfs')

    def configure(self, *args):
        '''Set the options for this initramfs from the passed arguments

        This converts the list of arguments into an options string for the
        preparer.

        '''

        self._options = ' '.join([ '--' + _ for _ in args ])

PREPARERS['genkernel'] = GenKernelPreparer
