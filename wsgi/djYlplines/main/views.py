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
from django.core.urlresolvers import reverse
import time
from django.db.models import Avg
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, render_to_response
from django.views import generic

from main.engine.smoothing import get_review_graph_data
from main.models import Business, Review
from .forms import FrontSearchForm
from .engine.search_businesses import search_for_businesses, get_business_reviews
# Create your views here.
"""
class IndexView(generic.DetailView):
    template_name = 'main/index.html'


class SearchResultsView(generic.ListView):
    template_name = 'main/results.html'


class BusinessView(generic.DetailView):
    template_name = 'main/business.html'
"""


def index(request):
    if 'query' in request.GET:
        form = FrontSearchForm(request.GET)
        if form.is_valid():
            print("form found valid")
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


def search_businesses(request):
    print("From search_businesses")
    return render(request, 'main/results.html')

def search_with_ajax(request):
    if 'query' in request.GET and 'location' in request.GET:
        form = FrontSearchForm(request.GET)
        if form.is_valid():
            print("form found valid from ajax")
            query = form.cleaned_data['query']
            location = form.cleaned_data['location']
            businesses = search_for_businesses(query, location)
            context = {
                'businesses': businesses,
                'form': form,
            }
            #time.sleep(5);
            return render_to_response("main/search_results_snippet.html",
                                      context)
        else:
            form = FrontSearchForm()
            return render_to_response("main/search_results_snippet.html", {'form': form})
    return render_to_response("main/search_results_snippet.html")

def retrieve_ylp_with_ajax(request):
    if 'business_id' in request.GET:
        business_id = request.GET.get('business_id')
        do_retrieve = int(request.GET.get('do_retrieve'))
        print(str(type(do_retrieve)))

        business = Business.objects.get(id=business_id)

        if do_retrieve == 1:
            get_business_reviews(business)

        ylpline_ratings, review_ratings, smooth_rating, sparkline, sparkline_6mo, sparkline_12mo, sparkline_24mo = get_review_graph_data(business)
        context = {
            'sparkline': sparkline,
            'sparkline_6mo': sparkline_6mo,
            'sparkline_12mo': sparkline_12mo,
            'sparkline_24mo': sparkline_24mo,
            'smooth_rating': smooth_rating,
        }
    return render_to_response("main/retrieve_ylp_snippet.html", context)

def business(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    get_business_reviews(business)
    reviews = Review.objects.filter(business=business).order_by('publish_date')
    ylpline_ratings, review_ratings, current_ylpline_rating, sparklines, sparklines_6mo, sparklines_12_mo, sparklines_24mo = get_review_graph_data(business)
    review_count = reviews.count()
    review_average = round(reviews.aggregate(Avg('rating'))['rating__avg'], 2)
    context = {'reviews': reviews,
               'review_count': review_count,
               'review_average': review_average,
               'current_ylpline_rating': current_ylpline_rating,
               'ylpline_ratings': ylpline_ratings,
               'review_ratings': review_ratings,
               }

    return render(request, 'main/business.html', context)
