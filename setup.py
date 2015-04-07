#!/usr/bin/env python
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of ckanext-ngsipreview.
#
# Ckanext-ngsipreview is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Ckanext-ngsipreview is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.

from setuptools import setup, find_packages


version = '0.2'

setup(
    name='ckanext-ngsipreview',
    version=version,
    description="",
    long_description='''CKAN extension that will give you the ability to generate real-time resources
    provided by a Context broker. Some resources may need your IDM token, so you must be logged in to
    be able to see those resources properly.
    ''',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Programming Language :: Python :: 2.7',
    ],

    author='Guillermo Zarzuelo',
    author_email='gzarrub@gmail.com',
    url='https://github.com/gzarrub/ckanext-ngsipreview',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.ngsipreview'],
    include_package_data=True,
    zip_safe=False,
    install_requires=['requests'],
    entry_points='''
        [ckan.plugins]
        # Add plugins here, e.g.
         ngsipreview=ckanext.ngsipreview.plugin:NGSIPreview
    ''',
)
