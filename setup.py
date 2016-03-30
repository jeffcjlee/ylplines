#!/usr/bin/env python

from setuptools import setup

setup(
    name='ylplines',
    version='0.0.1',
    description='Yelp trends',
    author='Jeff Lee',
    author_email='jeffcjlee@gmail.com',
    url='jeffcjlee.com',
    install_requires=[
        'Django==1.8.4',
        'psycopg2>=2.6.1',
        'yelp',
        'lxml==3.4.4',
        'beautifulsoup4',
        'requests-futures>=0.9.7',
        'coverage>=4.1b2',
        'coveralls',
    ],
    dependency_links=[
        'https://pypi.python.org/simple/django/'
    ],
)
