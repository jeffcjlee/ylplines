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
    url(r'^search/$', "main.views.search_with_ajax", name="search"),
    url(r'^retrieve_ylp/$', "main.views.retrieve_ylp_with_ajax", name="retrieve_ylp"),
    url(r'^enqueue_fetch/$', "main.views.enqueue_fetch_reviews_with_ajax",
        name="enqueue_fetch"),
    url(r'^check_fetch_state/$', "main.views.check_fetch_state_with_ajax",
        name="check_fetch_state"),
    url(r'^display_about/$', "main.views.display_about", name='display_about'),
    url(r'^about/$', views.about, name='about'),
]