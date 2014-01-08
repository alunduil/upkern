# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

from upkern.initramfs import PREPARERS

class DracutPreparer(object):
    pass

PREPARERS['dracut'] = DracutPreparer
