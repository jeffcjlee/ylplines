#!/usr/bin/env python
"""
ylplines - Clarity for Yelp
Copyright (C) 2016  Jeff Lee

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
"""Set up prerequisite packages and dependencies."""
from setuptools import setup

setup(
    name='ylplines',
    version='0.1.0',
    description='Yelp trends',
    author='Jeff Lee',
    author_email='jeffcjlee@gmail.com',
    url='jeffcjlee.com',
    install_requires=[
        'Django==1.8.4',
        'psycopg2>=2.6.1',
        'yelp',
        'lxml',
        'cssselect',
        'requests-futures>=0.9.7',
        'coverage>=4.1b2',
        'coveralls',
        'django-widget-tweaks',
        'Sphinx',
        'celery[redis]<4',
        'redis',
        'kombu',
        'amqp<2.0,>=1.4.9',
        'anyjson',
        'billiard',
        'newrelic',
    ],
    dependency_links=[
        'https://pypi.python.org/simple/django/'
    ],
)
