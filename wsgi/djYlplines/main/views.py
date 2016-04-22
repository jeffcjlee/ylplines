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
"""Views handler for 'main' Django application"""
import inspect

from django.shortcuts import render, render_to_response

from main.engine.smoothing import get_review_graph_data
from main.logging import log_exception
from main.models import Business
from main.forms import FrontSearchForm
from main.engine.search_businesses import search_for_businesses, update_business_reviews
from main import tasks

MODULE_NAME = 'main.views'

def index(request):
    """Renders front page of website"""
    try:
        if 'query' in request.GET:
            form = FrontSearchForm(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                location = form.cleaned_data['location']
                businesses = search_for_businesses(query, location)
                context = {
                    'businesses': businesses,
                    'form': form,
                }
                return render(request, 'main/index.html', context)
            else:
                form = FrontSearchForm()
        else:
            form = FrontSearchForm()
        return render(request, 'main/index.html', {'form': form})
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)


def search_with_ajax(request):
    """Handles ajax request when user searches"""
    try:
        if 'query' in request.GET and 'location' in request.GET:
            form = FrontSearchForm(request.GET)
            if form.is_valid():
                query = form.cleaned_data['query']
                location = form.cleaned_data['location']
                businesses = search_for_businesses(query, location)
                context = {
                    'businesses': businesses,
                    'form': form,
                }
                return render_to_response("main/search_results_snippet.html",
                                          context)
            else:
                form = FrontSearchForm()
                return render_to_response("main/search_results_snippet.html", {'form': form})
        return render_to_response("main/search_results_snippet.html")
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)


def retrieve_ylp_with_ajax(request):
    """Handles ajax request to fetch reviews for a business from the db"""
    try:
        if 'business_id' in request.GET:
            business_id = request.GET.get('business_id')
            business = Business.objects.get(id=business_id)

            update_business_reviews(business)

            ylpline_ratings, review_ratings, smooth_rating, sparkline, sparkline_6mo, sparkline_12mo, sparkline_24mo = get_review_graph_data(business)
            context = {
                'sparkline': sparkline,
                'sparkline_6mo': sparkline_6mo,
                'sparkline_12mo': sparkline_12mo,
                'sparkline_24mo': sparkline_24mo,
                'smooth_rating': smooth_rating,
                'ylpline_ratings': ylpline_ratings,
                'review_ratings': review_ratings,
            }
        return render_to_response("main/retrieve_ylp_snippet.html", context)
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)


def enqueue_fetch_reviews_with_ajax(request):
    """Handles ajax request to enqueue task to fetch reviews from Yelp"""
    try:
        if 'business_id' in request.GET:
            business_id = request.GET.get('business_id')
            task_result = tasks.enqueue_fetch_reviews.delay(business_id)
            task_id = task_result.id
            context = {
                'task_id': task_id,
            }
        return render_to_response("main/task_id_snippet.html",
                                  context)
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)


def check_fetch_state_with_ajax(request):
    """Handles ajax request to poll server on the status of a task"""
    try:
        if 'task_id' in request.GET:
            task_id = request.GET.get('task_id').rstrip()
            task_result = tasks.enqueue_fetch_reviews.AsyncResult(task_id)
            task_state = task_result.state
            task_progress = 0
            if type(task_result.info) == dict and 'current' in task_result.info:
                task_progress = task_result.info['current']
            elif task_state == 'SUCCESS':
                task_progress = 100
            print("TASK PROGRESS: " + str(task_progress))
            print("TASK STATE: " + task_state)
            context = {
                'task_state': '%s^%s' % (str(task_state), str(task_progress)),
            }
        return render_to_response("main/task_state_snippet.html", context)
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)
