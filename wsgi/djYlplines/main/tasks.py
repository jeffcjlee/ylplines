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
"""Async queue tasks for the main app"""
from __future__ import absolute_import

from celery import shared_task

import main.engine.search_businesses
#from main.engine.search_businesses import get_business_reviews
from main.models import Business


@shared_task
def enqueue_fetch_reviews(business_id, num_reviews=0):
    business = Business.objects.get(id=business_id)
    main.engine.search_businesses.get_business_reviews(business, num_reviews)
    return True


@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)