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
import io
import json
import os
import sys

#import grequests

from datetime import datetime, timedelta
from os import path
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from yelp.client import Client
from yelp.endpoint.search import Search
from yelp.oauth1_authenticator import Oauth1Authenticator

from main.models import Review, Business

"""
Take a search string and return a list of businesses.
Calls to Yelp API.
"""
# ==== CONSTANTS
NUM_REVIEWS_PER_PAGE = 20


def get_yelp_api_keys_filepath():
    """Helper method. Get Yelp API oAuth keys filepath"""
    base_path = path.dirname(__file__)
    file_path = path.abspath(path.join(base_path, '..', '..', '..', 'privatekeys', 'yelpAPI.json'))
    return file_path


def get_yelp_api_client():
    """Get the Yelp API client"""

    if 'OPENSHIFT_REPO_DIR' in os.environ or 'TRAVIS' in os.environ:
        auth = Oauth1Authenticator(
            consumer_key=os.environ['YELP_CONSUMER_KEY'],
            consumer_secret=os.environ['YELP_CONSUMER_SECRET'],
            token=os.environ['YELP_TOKEN'],
            token_secret=os.environ['YELP_TOKEN_SECRET']
        )
    else:
        file_path = get_yelp_api_keys_filepath()

        with io.open(file_path, 'r') as cred:
            creds = json.load(cred)
            auth = Oauth1Authenticator(**creds)

    client = Client(auth)
    return client


def save_business(id, name, image_url, url, review_count, rating):
    """Save or update a business to DB"""
    q_delim_index = url.find('?')
    url = url[:q_delim_index]  # Strip GET parameters

    if Business.objects.filter(id=id).exists():
        business = Business.objects.get(id=id)
        business.name = name
        business.image_url = image_url
        business.url = url
        business.review_count = review_count
        business.rating = rating
    else:
        business = Business(id=id,
                            name=name,
                            image_url=image_url,
                            url=url,
                            review_count=review_count,
                            rating=rating)
    business.save()


def search_for_businesses(query=""):
    """Search for businesses that match the search string and return a list of businesses"""
    print("Enter search_for_businesses")
    businesses = run_query(query)

    for cur_business in businesses:
        save_business(cur_business.id,
                      cur_business.name,
                      cur_business.image_url,
                      cur_business.url,
                      cur_business.review_count,
                      cur_business.rating)

    return businesses


def run_query(query):

    location = 'San Francisco'

    client = get_yelp_api_client()
    params = {
        'term': query,
    }
    print("before search")
    search = Search(client)
    response = search.search(location, **params)
    print("after search")
    businesses = response.businesses
    return businesses

#########################################################
#########################################################

def get_num_reviews_for_business(business, debug=False):
    if debug:
        business = Business.objects.get(id='tadu-ethiopian-kitchen-san-francisco-3')

    return business.review_count
    # urls = [business.url]
    # gre_request = (grequests.get(url) for url in urls)
    # response = grequests.map(gre_request)[0]
    # content = response.content
    # strainer = SoupStrainer(class_='tab-link tab-link--nav is-selected')
    # soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    # num_of_reviews = soup.find('span', class_='tab-link_count').get_text()
    # num_of_reviews = int(num_of_reviews[1:len(num_of_reviews)-1])
    # return num_of_reviews


def get_business_reviews(business, debug=False):
    if debug:
        business = Business.objects.get(id='blue-bottle-coffee-san-francisco-8')

    latest_review_date = None
    todays_date = datetime.today().date()

    if business.latest_review_pull and business.latest_review_pull + timedelta(days=7) >= todays_date:
        return

    if Review.objects.filter(business_id=business.id).exists():
        latest_review_date = Review.objects.filter(business_id=business.id).latest('publish_date').publish_date

    num_reviews = get_num_reviews_for_business(business)
    num_requests = num_reviews // NUM_REVIEWS_PER_PAGE
    if num_reviews % NUM_REVIEWS_PER_PAGE != 1:
        num_requests += 1
    print("Async pull start")
    urls = create_urls_list(business.url, num_reviews)
    #gre_request = (grequests.get(url) for url in urls)
    #responses = grequests.map(gre_request)
    responses = None
    print("Async pull end")

    print("Processing response (%s total)..." % num_requests, end="", flush=True)
    for ctr, response in enumerate(responses):
        print("%s..." % ctr, end="", flush=True)
        if response:
            if response.status_code == 200:
                process_async_response(response, business, latest_review_date)
            else:
                print("Retrieval unsuccessful, got a status code of: " + str(response.status_code))

    business.latest_review_pull = todays_date
    business.save()


def create_urls_list(business_url, num_reviews):
    """Generate the list of business URLs to extract reviews from given which async loop the program is on"""

    num_requests = num_reviews // NUM_REVIEWS_PER_PAGE
    if num_reviews % NUM_REVIEWS_PER_PAGE != 1:
        num_requests += 1
    urls = []

    for i in range(num_requests):
        start = i * NUM_REVIEWS_PER_PAGE
        urls.append(business_url + '?' + 'sort_by=date_desc' + '&' + 'start=' + str(start))
    return urls


def process_async_response(response, business, latest_review_date):
    content = response.content
    strainer = SoupStrainer(class_='review review--with-sidebar')
    soup = BeautifulSoup(content, 'lxml', parse_only=strainer)
    continue_review_retrieval = True

    raw_ids = soup.find_all('div', itemprop='review')
    raw_ratings = soup.find_all('meta', itemprop='ratingValue')
    raw_publish_dates = soup.find_all('meta', itemprop='datePublished')  # 2016-02-16
    raw_texts = soup.find_all('p', itemprop='description')

    ids = []
    ratings = []
    publish_dates = []
    texts = []

    for raw_id, raw_rating, raw_publish_date, raw_text in zip(raw_ids, raw_ratings, raw_publish_dates,
                                                              raw_texts):
        id = raw_id.attrs['data-review-id']
        if Review.objects.filter(id=id).exists():
            continue

        publish_date = raw_publish_date.attrs['content']
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d').date()
        if latest_review_date is not None and publish_date < latest_review_date:
            continue

        ids.append(id)
        ratings.append(raw_rating.attrs['content'])
        publish_dates.append(publish_date)
        texts.append(raw_text.get_text().replace(u'\xa0', u' '))

    if not ids:
        continue_review_retrieval = False
        return continue_review_retrieval

    for id, rating, publish_date, text in zip(ids, ratings, publish_dates, texts):
        if not Review.objects.filter(id=id).exists():
            review = Review(id=id, business=business, rating=rating, publish_date=publish_date, text=text)
            review.save()
    return continue_review_retrieval
