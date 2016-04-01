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

from lxml.cssselect import CSSSelector
from lxml.html import fromstring
from datetime import datetime, timedelta
import time
from timeit import default_timer
from os import path
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from requests_futures.sessions import FuturesSession
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


def search_for_businesses(query="", location=""):
    """Search for businesses that match the search string and return a list of businesses"""
    print("Enter search_for_businesses")
    businesses = run_query(query, location)

    for cur_business in businesses:
        save_business(cur_business.id,
                      cur_business.name,
                      cur_business.image_url,
                      cur_business.url,
                      cur_business.review_count,
                      cur_business.rating)

    return businesses


def run_query(query, location):

    #location = 'San Francisco'

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

def bg_cb(session, response):
    content = response.content

    tree = fromstring(content)
    sel = CSSSelector('div.review.review--with-sidebar:not(.js-war-widget)')
    ids = [e.get('data-review-id') for e in sel(tree)]

    sel = CSSSelector('div.review.review--with-sidebar:not(.js-war-widget) meta[itemprop="ratingValue"]')
    ratings = [e.get('content') for e in sel(tree)]

    sel = CSSSelector('div.review.review--with-sidebar:not(.js-war-widget) meta[itemprop="datePublished"]')

    #publish_dates = [e.get('content') for e in sel(tree)]
    publish_dates = []
    for e in sel(tree):
        publish_date = e.get('content')
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d').date()
        publish_dates.append(publish_date)


    sel = CSSSelector('p[itemprop="description"]')
    texts = []
    #texts = [e.text for e in sel(tree)]
    for e in sel(tree):
        #text = e.replace(u'\xa0', u' ')
        texts.append(e)
    #texts.append(raw_text.get_text().replace(u'\xa0', u' '))



    response.data = [ids, ratings, publish_dates, texts]
    """
    strainer_start = time.clock()
    strainer = SoupStrainer(class_='review review--with-sidebar')
    strainer_end = time.clock()
    souping_start = time.clock()
    soup = BeautifulSoup(content, 'lxml', parse_only=strainer, from_encoding='UTF-8')
    #soup = BeautifulSoup(content, 'lxml', from_encoding='UTF-8')
    souping_end = time.clock()
   # print("Internal souping duration: " + str(souping_end-souping_start))
    # continue_review_retrieval = True
    #print("Soup!::: ")
    #print(soup.prettify())
    raw_ids = []
    raw_ratings = []
    raw_publish_dates = []
    raw_texts = []
    id_find_start = time.clock()
    raw_ids = soup.find_all('div', itemprop='review')
    id_find_end = time.clock()
    rating_find_start = time.clock()
    raw_ratings = soup.find_all('meta', itemprop='ratingValue')
    rating_find_end = time.clock()
    date_find_start = time.clock()
    raw_publish_dates = soup.find_all('meta', itemprop='datePublished')  # 2016-02-16
    date_find_end = time.clock()
    text_find_start = time.clock()
    raw_texts = soup.find_all('p', itemprop='description')
    text_find_end = time.clock()
    #print(str(raw_ids))
    #print(str(raw_ratings))
    #print(str(raw_publish_dates))
    #print(str(raw_texts))
    ids = []
    ratings = []
    publish_dates = []
    texts = []

    forloop_start = time.clock()
    for raw_id, raw_rating, raw_publish_date, raw_text in zip(raw_ids, raw_ratings, raw_publish_dates,
                                                              raw_texts):
        id = raw_id.attrs['data-review-id']
        #print(str(id))
        #if Review.objects.filter(id=id).exists(): # TODO TURN THESE BACK ON
        #    continue

        publish_date = raw_publish_date.attrs['content']
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d').date()

        ids.append(id)
        ratings.append(raw_rating.attrs['content'])
        publish_dates.append(publish_date)
        texts.append(raw_text.get_text().replace(u'\xa0', u' '))
    forloop_end = time.clock()
    #print(str(ids))
    #print(str(ratings))
    #print(str(publish_dates))
    response.data = [ids, ratings, publish_dates, texts,
                     strainer_end-strainer_start,
                     souping_end-souping_start,
                     id_find_end-id_find_start,
                     rating_find_end-rating_find_start,
                     date_find_end-date_find_start,
                     text_find_end-text_find_start,
                     forloop_end-forloop_start
    ]
    #print(str(response.data))
    """



def get_business_reviews(business, debug=False):
    if debug:
        business = Business.objects.get(id='blue-bottle-coffee-san-francisco-8')

    latest_review_date = None
    todays_date = datetime.today().date()

    #if business.latest_review_pull and business.latest_review_pull + timedelta(days=7) >= todays_date:
    #    return

    if Review.objects.filter(business_id=business.id).exists():
        latest_review_date = Review.objects.filter(business_id=business.id).latest('publish_date').publish_date

    num_reviews = get_num_reviews_for_business(business)
    num_requests = num_reviews // NUM_REVIEWS_PER_PAGE
    if num_reviews % NUM_REVIEWS_PER_PAGE != 1:
        num_requests += 1
    print("Concurrent pull start")
    concurrency_pull_start = default_timer()
    urls = create_urls_list(business.url, num_reviews)
    MAX_WORKERS = 50 #max(urls.__len__()//3, 20)
    spoolup_start = default_timer()
    session = FuturesSession(max_workers=MAX_WORKERS)
    spoolup_end = default_timer()
    print("Spoolup : %s" % str(spoolup_end-spoolup_start))
    futures = []
    responses = []
    print('sending out...', end="", flush=True)
    for i, url in enumerate(urls):
        print(str(i) + '...', end="", flush=True)
        future = session.get(url, background_callback=bg_cb)
        futures.append(future)

    print("")

    print('response receivedd...', end="", flush=True)
    for i, future in enumerate(futures, 1):
        response = future.result()
        responses.append(response)
        print(str(i) + ": " + str(response.status_code) + '...', end="", flush=True)

    concurrency_pull_end = default_timer()
    print("Concurrent pull end.")
    print('Concurrency pull duration: %s seconds' % str(concurrency_pull_end-concurrency_pull_start))

    print('Begin response processing')
    print("Processing response (%s total)..." % num_requests, end="", flush=True)
    strainer_dur = 0.0
    souping_dur = 0.0
    id_find_dur = 0.0
    rating_find_dur = 0.0
    date_find_dur = 0.0
    text_find_dur = 0.0
    forloop_dur = 0.0

    process_start = default_timer()
    for ctr, response in enumerate(responses, 1):
        print("%s..." % ctr, end="", flush=True)
        if response:
            if response.status_code == 200:
                """
                strainer_dur += response.data[4]
                souping_dur += response.data[5]
                id_find_dur += response.data[6]
                rating_find_dur += response.data[7]
                date_find_dur += response.data[8]
                text_find_dur += response.data[9]
                forloop_dur += response.data[10]
                """

                process_async_response(response, business, latest_review_date)
            else:
                print("Retrieval unsuccessful, got a status code of: " + str(response.status_code))
    process_end = default_timer()
    print('\nResponse processing duration: %s seconds' % str(process_end-process_start))

    """
    print("Strainer init duration: " + str(strainer_dur) )
    print("Souping duration: " +str(souping_dur))
    print("id find duration: " +str(id_find_dur))
    print("rating find duration: " +str(rating_find_dur))
    print("date find duration: " +str(date_find_dur))
    print("text find duration: " +str(text_find_dur))
    print("forloop duration: " +str(forloop_dur))
    """

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
    """
    content = response.content
    strainer = SoupStrainer(class_='review review--with-sidebar')
    soup = BeautifulSoup(content, 'lxml', parse_only=strainer, from_encoding='UTF-8')
    #continue_review_retrieval = True

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
    """
    ids = response.data[0]
    ratings = response.data[1]
    publish_dates = response.data[2]
    texts = response.data[3]


    #print(str(ids))
    #print(str(ratings))
    #print(str(publish_dates))
    #print(str(texts))
    for id, rating, publish_date, text in zip(ids, ratings, publish_dates, texts):
        if not Review.objects.filter(id=id).exists():
            if latest_review_date is not None and publish_date < latest_review_date:
                continue
            review = Review(id=id, business=business, rating=rating, publish_date=publish_date, text=text)
            review.save()
    #return continue_review_retrieval
