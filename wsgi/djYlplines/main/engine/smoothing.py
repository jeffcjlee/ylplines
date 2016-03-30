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
from datetime import datetime
from decimal import Decimal

from main.models import Review, Business


def get_review_graph_data(business, debug=False):
    if debug:
        business = Business.objects.filter(id='blue-bottle-coffee-san-francisco-8')
    print(str(business))
    reviews = Review.objects.filter(business=business).order_by('publish_date')
    SMOOTH_FACTOR = 0.25

    ylpline_ratings = []
    review_ratings = []
    review = reviews[0]
    publish_date = review.publish_date
    actual_rating = float(review.rating)
    smooth_rating = float(review.rating)

    publish_datetime = datetime(publish_date.year, publish_date.month, publish_date.day)
    #epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = datetime(1970, 1, 1)
    publish_since_epoch = (publish_datetime - epoch).total_seconds() * 1000

    ylpline_ratings.append([publish_since_epoch, smooth_rating])
    review_ratings.append([publish_since_epoch, actual_rating])
    # g_data = {review.id: (review.publish_date, actual_rating, smooth_rating)}
    prev_smooth_rating = smooth_rating

    for review in reviews[1:]:
        publish_date = review.publish_date
        publish_datetime = datetime(publish_date.year, publish_date.month, publish_date.day)
        publish_since_epoch = (publish_datetime - epoch).total_seconds() * 1000

        actual_rating = float(review.rating)
        smooth_rating = float(prev_smooth_rating + SMOOTH_FACTOR * (actual_rating-prev_smooth_rating))

        #g_data[review.id] = (review.publish_date, actual_rating, smooth_rating)
        ylpline_ratings.append([publish_since_epoch, smooth_rating])
        review_ratings.append([publish_since_epoch, actual_rating])

        prev_smooth_rating = smooth_rating

    #series_data = [{'name': 'ylpline rating', 'data': ylpline_ratings},
    #              {'name': 'review rating', 'data': review_ratings}]

    #print(str(ylpline_ratings))
    #print(str(sorted(g_data.items())))
    return (ylpline_ratings, review_ratings)

