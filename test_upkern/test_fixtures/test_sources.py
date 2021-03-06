# Copyright (C) 2014 by Alex Brandt <alunduil@alunduil.com>
#
# upkern is freely distributable under the terms of an MIT-style license.
# See COPYING or http://www.opensource.org/licenses/mit-license.php.

SOURCES = {}

SOURCES['correct'] = []

SOURCES['correct'].append(
    {
        'name': None,
        'directory_name': 'linux-3.12.6-gentoo',
        'package_name': '=sys-kernel/gentoo-sources-3.12.6',
        'binary_name': 'bzImage-3.12.6-gentoo',
        'configuration_name': 'config-3.12.6-gentoo',
        'system_map_name': 'System.map-3.12.6-gentoo',
        'kernel_index': 3012006000,
        'kernel_suffix': '-3.12.6-gentoo',
        'portage_configuration': { 'MAKEOPTS': '-j5' },
        'source_directories': [
            'linux-3.12.6-gentoo',
            'linux-3.12.5-gentoo',
            'linux-3.10.7-gentoo',
        ],
        'configuration_files': [
            'config-3.12.6-gentoo',
            'config-3.12.5-gentoo',
            'config-3.10.7-gentoo',
        ],
        'package_names': [
            'sys-kernel/gentoo-sources-3.12.6',
            'sys-kernel/gentoo-sources-3.12.5',
            'sys-kernel/gentoo-sources-3.10.7',
        ],
    })

SOURCES['correct'].append(
    {
        'name': 'sys-kernel/gentoo-sources-3.12.6',
        'directory_name': 'linux-3.12.6-gentoo',
        'package_name': '=sys-kernel/gentoo-sources-3.12.6',
        'binary_name': 'bzImage-3.12.6-gentoo',
        'configuration_name': 'config-3.12.6-gentoo',
        'system_map_name': 'System.map-3.12.6-gentoo',
        'kernel_index': 3012006000,
        'kernel_suffix': '-3.12.6-gentoo',
        'portage_configuration': { 'MAKEOPTS': '-j5' },
        'source_directories': [
            'linux-3.12.6-gentoo',
            'linux-3.12.5-gentoo',
            'linux-3.10.7-gentoo',
        ],
        'configuration_files': [
            'config-3.12.6-gentoo',
            'config-3.12.5-gentoo',
            'config-3.10.7-gentoo',
        ],
        'package_names': [
            'sys-kernel/gentoo-sources-3.12.6',
            'sys-kernel/gentoo-sources-3.12.5',
            'sys-kernel/gentoo-sources-3.10.7',
        ],
    })

SOURCES['correct'].append(
    {
        'name': 'gentoo-sources-3.9.11-r1',
        'directory_name': 'linux-3.9.11-gentoo-r1',
        'package_name': '=sys-kernel/gentoo-sources-3.9.11-r1',
        'binary_name': 'bzImage-3.9.11-gentoo-r1',
        'configuration_name': 'config-3.9.11-gentoo-r1',
        'system_map_name': 'System.map-3.9.11-gentoo-r1',
        'kernel_index': 3009011001,
        'kernel_suffix': '-3.9.11-gentoo-r1',
        'portage_configuration': { 'MAKEOPTS': '-j5' },
        'source_directories': [
            'linux-3.12.6-gentoo',
            'linux-3.12.5-gentoo',
            'linux-3.10.7-gentoo',
            'linux-3.9.11-gentoo-r1',
        ],
        'configuration_files': [
            'config-3.12.6-gentoo',
            'config-3.12.5-gentoo',
            'config-3.10.7-gentoo',
            'config-3.9.11-gentoo-r1',
        ],
        'package_names': [
            'sys-kernel/gentoo-sources-3.12.6',
            'sys-kernel/gentoo-sources-3.12.5',
            'sys-kernel/gentoo-sources-3.10.7',
            'sys-kernel/gentoo-sources-3.9.11-r1',
        ],
    })

SOURCES['correct'].append(
    {
        'name': 'hardened-sources-3.11.7-r1',
        'directory_name': 'linux-3.11.7-hardened-r1',
        'package_name': '=sys-kernel/hardened-sources-3.11.7-r1',
        'binary_name': 'bzImage-3.11.7-hardened-r1',
        'configuration_name': 'config-3.11.7-hardened-r1',
        'system_map_name': 'System.map-3.11.7-hardened-r1',
        'kernel_index': 3011007001,
        'kernel_suffix': '-3.11.7-hardened-r1',
        'portage_configuration': { 'MAKEOPTS': '-j5' },
        'source_directories': [
            'linux-3.12.6-gentoo',
            'linux-3.12.5-gentoo',
            'linux-3.11.7-hardened-r1',
            'linux-3.10.7-gentoo',
        ],
        'configuration_files': [
            'config-3.12.6-gentoo',
            'config-3.12.5-gentoo',
            'config-3.11.7-hardened-r1',
            'config-3.10.7-gentoo',
        ],
        'package_names': [
            'sys-kernel/gentoo-sources-3.12.6',
            'sys-kernel/gentoo-sources-3.12.5',
            'sys-kernel/hardened-sources-3.11.7-r1',
            'sys-kernel/gentoo-sources-3.10.7',
        ],
    })

SOURCES['all'] = []
SOURCES['all'].extend(SOURCES['correct'])
