# Copyright (C) 2013 by Alex Brandt <alunduil@alunduil.com>
#
# crumbs is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

# -----------------------------------------------------------------------------
import sys
import traceback

if sys.version_info.major < 3:
    import ConfigParser
    configparser_name = 'ConfigParser'
else:
    import configparser
    configparser_name = 'configparser'

original_sections = sys.modules[configparser_name].ConfigParser.sections

def monkey_sections(self):
    '''Return a list of sections available; DEFAULT is not included in the list.

    Monkey patched to exclude the nosetests section as well.

    '''

    _ = original_sections(self)

    if any([ 'distutils/dist.py' in frame[0] for frame in traceback.extract_stack() ]) and _.count('nosetests'):
        _.remove('nosetests')

    return _

sys.modules[configparser_name].ConfigParser.sections = monkey_sections
# -----------------------------------------------------------------------------

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

from upkern import information

PARAMS = {}

PARAMS['name'] = information.NAME
PARAMS['version'] = information.VERSION
PARAMS['description'] = information.DESCRIPTION

with open('README.rst', 'r') as fh:
    PARAMS['long_description'] = fh.read()

PARAMS['author'] = information.AUTHOR
PARAMS['author_email'] = information.AUTHOR_EMAIL
PARAMS['url'] = information.URL
PARAMS['license'] = information.LICENSE

PARAMS['classifiers'] = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: System :: Operating System Kernels :: Linux',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        ]

PARAMS['keywords'] = [
        'gentoo',
        'kernel',
        'update',
        ]

PARAMS['provides'] = [
        'upkern',
        ]

with open('requirements.txt', 'r') as req_fh:
    PARAMS['install_requires'] = req_fh.readlines()

with open('test_upkern/requirements.txt', 'r') as req_fh:
    PARAMS['tests_require'] = req_fh.readlines()

PARAMS['test_quite'] = 'nose.collector'

PARAMS['entry_points'] = {
        'console_scripts': [
            'upkern = upkern:run',
            ],
        }

PARAMS['packages'] = [
        'upkern',
        'upkern.kernel',
        'upkern.bootloaders',
        'upkern.system',
        ]

PARAMS['data_files'] = [
        ('share/doc/{P[name]}-{P[version]}'.format(P = PARAMS), [
            'README.rst',
            ]),
        ]

setup(**PARAMS)
