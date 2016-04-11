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
"""URLs controller for 'main' Django application"""
from django.conf.urls import url

from main import views

urlpatterns = [
    url(r'^/?$', views.index, name='index'),
    url(r'^business/(?P<business_id>.+)/$', views.business, name='business'),
    url(r'^search/$', "main.views.search_with_ajax", name="search"),
    url(r'^retrieve_ylp/$', "main.views.retrieve_ylp_with_ajax", name="retrieve_ylp"),
]