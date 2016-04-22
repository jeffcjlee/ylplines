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
"""Module stores functions that help with logging"""
import logging


def log_exception(module, method, ex):
    """Log a raised exception that has been caught."""
    logging.exception('Exception was caught in "%s.%s" with details: %s' %
          (module, method, str(type(ex)) + str(ex)))


def log_error(module, method, err):
    """Log an error that has been raised."""
    print('Error raised in "%s.%s" with details: %s' % (module, method, err))


def log(module, method, msg):
    """Log a logging message."""
    print('LOG (%s.%s): %s' % (module, method, msg))
