from django.conf.urls import url

from . import views

# urlpatterns = [
#     url(r'^$', views.IndexView.as_view(), name='index'),
#     url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
#     url(r'^(?P<pk>[0-9]+)/results/$', views.ResultsView.as_view(), name='results'),
#     url(r'^(?P<question_id>[0-9]+)/vote/$', views.vote, name='vote'),
# ]

urlpatterns = [
    url(r'^/?$', views.index, name='index'),
    url(r'^results$', views.search_businesses, name='results'),
    url(r'^business/(?P<business_id>.+)/$', views.business, name='business'),
    url(r'^search/$', "main.views.search_with_ajax", name="search"),
    url(r'^retrieve_ylp/$', "main.views.retrieve_ylp_with_ajax", name="retrieve_ylp"),
]