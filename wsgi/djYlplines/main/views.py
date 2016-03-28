from django.shortcuts import render
from django.views import generic
from .forms import FrontSearchForm

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
    front_search_form = FrontSearchForm()
    return render(request, 'main/index.html', {'front_search_form': front_search_form})


def search_businesses(request):
    return render(request, 'main/results.html')


def business(request):
    return render(request, 'main/business.html')
