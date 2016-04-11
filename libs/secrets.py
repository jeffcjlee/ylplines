# ylplines - Clarity for Yelp
# Copyright (C) 2016  Jeff Lee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Generates secret key for authentication purposes in Django."""
import json

__secrets = {
    'secret_key': 'a',
}


def getter(path):
    """Get a json file's contents."""
    try:
        with open(path) as handle:
            return json.load(handle)
    except IOError:
        return __secrets


def generator():
    """Generate secret key to be used for authentication."""

    # Based on Django's SECRET_KEY hash generator
    # https://github.com/django/django/blob/9893fa12b735f3f47b35d4063d86dddf3145cb25/django/core/management/commands/startproject.py

    from django.utils.crypto import get_random_string
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    __secrets['secret_key'] = get_random_string(50, chars)

    return __secrets

if __name__ == '__main__':
    data = json.dumps(generator())
    print(data)
