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
"""Module handles all communication and fetching actions with Yelp."""
import inspect
import io
import json
import os
from time import sleep

from lxml.cssselect import CSSSelector
from lxml.html import fromstring
from datetime import datetime, timedelta
from timeit import default_timer
from os import path
from requests_futures.sessions import FuturesSession
from yelp.client import Client
from yelp.endpoint.search import Search
from yelp.oauth1_authenticator import Oauth1Authenticator

import main.tasks
from main.logging import log_exception, log, log_error
from main.models import Review, Business

# ==== CONSTANTS
# Name of module for logging purposes.
MODULE_NAME = 'search_businesses'
# Yelp only shows 20 reviews per page request.
NUM_REVIEWS_PER_PAGE = 20
# How long since a business' last fetching should we wait before
# bothering to fetch again.
DAYS_TO_DELAY_FETCHING = 0
# The number of max slave thread workers to be allowed to concurrently exist.
MAX_WORKERS = 5

#########################################################
# Search for businesses when given search query
#########################################################


def search_for_businesses(query="", location="", debug=False):
    """
    Search for businesses that match against search terms and return
    a list of businesses.

    :param: query: Search terms
    :param: location: Geographical location to search in or near
    :return: A list of Businesses
    """
    FUNC_NAME = inspect.currentframe().f_code.co_name

    if debug:
        location = 'San Francisco'
    elif location == "":
        log_error(MODULE_NAME, FUNC_NAME,
                  'No location input in search')
        return []

    businesses = []
    log(MODULE_NAME,
        FUNC_NAME,
        'query: "%s", location: "%s"' % (query, location))

    try:
        businesses = run_query(query, location)
    except Exception as ex:
        log_exception(MODULE_NAME, FUNC_NAME, ex)

    # First 10 entries. No pagination yet so KISS.
    businesses = businesses[:10]
    for cur_business in businesses:
        has_reviews = Review.objects.filter(
            business_id=cur_business.id
        ).exists()
        cur_business.has_reviews = has_reviews

        save_business(cur_business.id,
                      cur_business.name,
                      cur_business.image_url,
                      cur_business.url,
                      cur_business.review_count,
                      cur_business.rating)
    return businesses


def save_business(id, name, image_url, url, review_count, rating):
    """
    Save or update a business to database

    :param: id: Business ID
    :param: name: Business name
    :param: image_url: URL to a business image
    :param: url: URL to the business on Yelp
    :param: review_count: Number of reviews for the business on Yelp
    :param: rating: Yelp review rating of business
    """
    FUNC_NAME = inspect.currentframe().f_code.co_name

    q_delim_index = url.find('?')
    url = url[:q_delim_index]  # Strip GET parameters

    # Update existing business in database
    try:
        if Business.objects.filter(id=id).exists():
            business = Business.objects.get(id=id)
            business.name = name
            business.image_url = image_url
            business.url = url
            business.review_count = review_count
            business.rating = rating
            log(MODULE_NAME, FUNC_NAME, 'Updating business to db: %s' %
                business.id)
        # Save new business
        else:
            business = Business(id=id,
                                name=name,
                                image_url=image_url,
                                url=url,
                                review_count=review_count,
                                rating=rating)
            log(MODULE_NAME, FUNC_NAME, 'Creating new business to db: %s' % (
                business.id))
        business.save()
    except Exception as ex:
        log_exception(MODULE_NAME, FUNC_NAME, ex)


def run_query(query, location):
    """
    Execute search query to Yelp.

    :param: query: Search terms
    :param: location: Geographical location to search for
    :return: A list of Businesses
    """
    FUNC_NAME = inspect.currentframe().f_code.co_name

    if location == "":
        log_error(MODULE_NAME, FUNC_NAME, 'No location input provided.')
        return []

    client = get_yelp_api_client()
    if not client:
        return []

    # Yelp takes search term query in params kwargs,
    # and location directly as a param in search fxn.
    params = {
        'term': query,
    }

    try:
        search = Search(client)
        response = search.search(location, **params)
    except Exception as ex:
        log_exception(MODULE_NAME, FUNC_NAME, ex)

    businesses = response.businesses
    if not businesses:
        businesses = []
    return businesses


def get_yelp_api_keys_filepath():
    """
    Get Yelp API oAuth keys filepath.

    Only used for local usage of Yelp API.

    :return: Filepath of API keys.
    :rtype: str
    """
    base_path = path.dirname(__file__)
    file_path = path.abspath(path.join(base_path, '..', '..', '..',
                                       'privatekeys', 'yelpAPI.json'))
    return file_path


def get_yelp_api_client():
    """
    Get the Yelp API client

    :return: Yelp API client
    :rtype: Yelp Client
    """
    FUNC_NAME = inspect.currentframe().f_code.co_name

    try:
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
    except Exception as ex:
        log_exception(MODULE_NAME, FUNC_NAME, ex)

    return client


#########################################################
# Fetch reviews from a business
#########################################################


def get_num_reviews_for_business(business, debug=False):
    """
    Retrieves the number of reviews a business in the database has.

    :param: business: The business to retrieve number of reviews in Yelp for.
    Must be in database.
    :param: debug: True if debug mode is on.
    :return: The number of reviews the business has in Yelp.
    """
    if debug:
        business = Business.objects.get(
            id='tadu-ethiopian-kitchen-san-francisco-3')
    return business.review_count


def parse_results_in_background(session, response):
    """
    Parse HTML of request results in order to get review data from a Yelp page.

    Is executed in background by a slave thread.
    Uses lxml HTML parser to find required ratings/review data
    from the Yelp website.
    Be mindful: parsing matches against exact DOM names found in Yelp website.
    If they decide to change a DOM element name or the DOM structure,
    this function must be updated.

    Collects all review IDs, review ratings, and review publish dates into
    their own respective lists.
    It then appends them to response.data to be consumed by the master thread.

    :param session: The http session this request lives in
    :param response: The http response provided by Yelp
    :return: Nothing. Appends data to response.data.
    """
    content = response.content

    tree = fromstring(content)
    sel = CSSSelector('div.review.review--with-sidebar:not(.js-war-widget)')
    ids = [e.get('data-review-id') for e in sel(tree)]

    sel = CSSSelector(
        'div.review.review--with-sidebar:not(.js-war-widget) meta[itemprop="ratingValue"]')
    ratings = [e.get('content') for e in sel(tree)]

    sel = CSSSelector('div.review.review--with-sidebar:not(.js-war-widget) meta[itemprop="datePublished"]')

    publish_dates = []
    for e in sel(tree):
        publish_date = e.get('content')
        publish_date = datetime.strptime(publish_date, '%Y-%m-%d').date()
        publish_dates.append(publish_date)

    # Comment out collecting review text. Maybe in the future we may need this.
    # sel = CSSSelector('p[itemprop="description"]')
    # texts = []
    # for e in sel(tree):
    #    #text = e.replace(u'\xa0', u' ')
    #    texts.append(e)
    # texts.append(raw_text.get_text().replace(u'\xa0', u' '))

    response.data = [ids, ratings, publish_dates]  # ,texts]


def get_business_reviews(business, num_reviews=0, task=None, debug=False):
    """
    Fetches business reviews for a single business and saves it to the database.

    This is a computationally intensive function that makes multiple requests
    to the Yelp website and collect reviews for a business. Yelp restricts
    the number of reviews per page, so multiple threads must call multiple
    requests to collect all business reviews. If a business has 500 reviews,
    and Yelp only shows 20 reviews per page, 25 http requests must be made to
    Yelp.

    In the background of each thread, it parses the response HTML content to
    get the relevant review data for consumption.

    Warning: You must not set the # of max thread workers to be unreasonably
    high. This will cause an out of memory error in production and cause the
    production server to crash and restart.

    :param business: The business to fetch reviews for.
    :param num_reviews: If provided, will only get the number of reviews,
    most recent first. Otherwise, will fetch all reviews of a business.
    :param debug: Debug mode is on if True.
    :return: Nothing. Reviews are saved into the database.
    """
    FUNC_NAME = inspect.currentframe().f_code.co_name
    do_not_store_latest_pull = False
    print("task for " + business.id + " is: " + str(task))
    if debug:
        business = Business.objects.get(id='girl-and-the-goat-chicago')
    if not business:
        return

    """
    if task:
        fake_fetch(task)
        return
    """

    latest_review_date = None
    todays_date = datetime.today().date()

    # Don't bother fetching if we fetched recently already.
    if business.latest_review_pull and business.latest_review_pull + \
            timedelta(days=DAYS_TO_DELAY_FETCHING) >= todays_date:
        print("Hitting too recent to fetch")
        log(MODULE_NAME, FUNC_NAME, '%s | Hitting too recent to fetch' %
            business.id)
        return

    if Review.objects.filter(business_id=business.id).exists():
        latest_review_date = Review.objects.filter(
            business_id=business.id
        ).latest('publish_date').publish_date

    if num_reviews <= 0:
        num_reviews = get_num_reviews_for_business(business)
    num_requests = num_reviews // NUM_REVIEWS_PER_PAGE
    if num_reviews % NUM_REVIEWS_PER_PAGE != 0:
        num_requests += 1

    log(MODULE_NAME, FUNC_NAME, '%s | Concurrent pull start' % business.id)
    concurrency_pull_start = default_timer()
    urls = create_urls_list(business.url, num_reviews)
    session = FuturesSession(max_workers=MAX_WORKERS)
    futures = []
    responses = []

    # Multi-thread requests and HTML parsing
    for i, url in enumerate(urls):
        future = session.get(url,
                             background_callback=parse_results_in_background)
        futures.append(future)

    # Wait for callbacks to finish
    print('Response received...', end="", flush=True)
    for i, future in enumerate(futures, 1):
        response = future.result()
        responses.append(response)
        progress = round(i * 90 / futures.__len__(), 1)
        if task:
            task.update_state(state='PROGRESS', meta={'current': progress})
        print(str(i) + ": " + str(response.status_code) + " " + str(response.reason) + '...', end="", flush=True)

    concurrency_pull_end = default_timer()
    log(MODULE_NAME, FUNC_NAME, '%s | Concurrent pull end. Duration: %s '
                                'seconds' % (business.id, str(concurrency_pull_end-concurrency_pull_start)))
    # Save reviews to database
    log(MODULE_NAME, FUNC_NAME, '%s | Begin response processing' % business.id)
    print("Processing response (%s total)..." % num_requests, end="", flush=True)

    process_start = default_timer()
    for ctr, response in enumerate(responses, 1):
        print("%s..." % ctr, end="", flush=True)
        if response:
            if response.status_code == 200:
                save_reviews(response, business, latest_review_date)
            else:
                do_not_store_latest_pull = True
                log_error(MODULE_NAME, FUNC_NAME, 'Fetch unsuccessful. Got an HTTP status code of: %s'
                          % str(response.status_code))
        progress = 90 + (round(i * 10 / responses.__len__(), 1))
        if task:
            print("theres a task!")
            task.update_state(state='PROGRESS', meta={'current': progress})
    process_end = default_timer()
    log(MODULE_NAME, FUNC_NAME, '\nProcessing response duration: %s seconds'
        % str(process_end-process_start))

    # Update business that we fetched reviews today
    if not do_not_store_latest_pull:
        business.latest_review_pull = todays_date
        business.save()


def fake_fetch(task=None):
    TOTAL = 10
    print("in fake fetch!")
    for i in range(1, TOTAL):
        sleep(1)
        progress = i*90//TOTAL
        if task:
            task.update_state(state='PROGRESS', meta={'current': progress})

    for i in range(1, TOTAL):
        sleep(0.1)
        progress = 90 + (i*10//TOTAL)
        if task:
            task.update_state(state='PROGRESS', meta={'current': progress})


def create_urls_list(business_url, num_reviews):
    """
    Generate the list of business URLs to extract reviews from given
    which async loop the program is on

    :param: business_url: URL to main business page on Yelp
    :param: num_reviews: number of reviews the business has on Yelp
    :return: A list of URLs
    """
    num_requests = num_reviews // NUM_REVIEWS_PER_PAGE
    if num_reviews % NUM_REVIEWS_PER_PAGE != 1:
        num_requests += 1
    urls = []

    # Must have sort order to be date descending (most recent first).
    for i in range(num_requests):
        start = i * NUM_REVIEWS_PER_PAGE
        urls.append(business_url + '?' + 'sort_by=date_desc' + '&' + 'start=' + str(start))
    return urls


def save_reviews(response, business, latest_review_date):
    """
    Save reviews to database.

    :param response: Holds review data
    :param business: The business the reviews are for
    :param latest_review_date: The most recent date we fetched for reviews
    for the business
    :return: Nothing. Reviews are saved to database.
    """
    ids = response.data[0]
    ratings = response.data[1]
    publish_dates = response.data[2]
    #texts = response.data[3]

    try:
        for id, rating, publish_date in zip(ids, ratings, publish_dates):
            # Don't bother to save if the review already exists in db.
            if not Review.objects.filter(id=id).exists():
                # Quit out if the publish date is older than the last fetch date
                # since everything in the loop now will be older than the last
                # fetch date.
                if latest_review_date is not None and publish_date < latest_review_date:
                    continue
                review = Review(id=id, business=business, rating=rating, publish_date=publish_date)
                review.save()

        # Save for in case we want to store text
        # for id, rating, publish_date, text in zip(ids, ratings, publish_dates, texts):
        #     if not Review.objects.filter(id=id).exists():
        #         if latest_review_date is not None and publish_date < latest_review_date:
        #             continue
        #         review = Review(id=id, business=business, rating=rating, publish_date=publish_date, text=text)
        #         review.save()
    except Exception as ex:
        log_exception(MODULE_NAME, inspect.currentframe().f_code.co_name, ex)


def update_business_reviews(business, debug=False):
    """Checks if a business needs to fetch more reviews that the db does not
    hold and fetches them from Yelp

    :param business: The business to update reviews for in the db
    :return: Nothing.
    """

    if debug:
        business = Business.objects.get(
            id='tadu-ethiopian-kitchen-san-francisco-3')
    num_reviews_in_business = get_num_reviews_for_business(business)
    num_reviews_in_db = Review.objects.filter(business=business).count()
    num_reviews_diff = num_reviews_in_business - num_reviews_in_db

    log(MODULE_NAME, inspect.currentframe().f_code.co_name, '%s | # reviews: '
                                                            '%s, # in db: %s, difference of: %s' %
        (business.id, str(num_reviews_in_business), str(num_reviews_in_db), str(num_reviews_diff)))
    if num_reviews_diff > 0:
        if num_reviews_diff <= 100:
            # get a num of pages worth of reviews for business, no queueing
            get_business_reviews(business, num_reviews_diff)
        else:
            # enqueue to update a business with a num of pages worth of
            # reviews, queue
            main.tasks.enqueue_fetch_reviews.delay(business.id,
                                                   num_reviews_diff)





