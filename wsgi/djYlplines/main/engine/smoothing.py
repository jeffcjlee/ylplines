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
from datetime import datetime, timedelta
from decimal import Decimal

from main.models import Review, Business


def get_review_graph_data(business, debug=False):
    if debug:
        business = Business.objects.filter(id='whitewater-excitement-lotus-2')
    print(str(business))
    reviews = Review.objects.filter(business=business).order_by('publish_date')
    SMOOTH_FACTOR = 0.2

    ylpline_ratings = []
    review_ratings = []
    review = reviews[0]
    publish_date = review.publish_date
    actual_rating = float(review.rating)
    smooth_rating = float(review.rating)

    #print("publish_date type: " + str(type(publish_date)))
    today = datetime.today().date()
    #sparkline
    one_spark_unit_ago = today - timedelta(days=18)
    two_spark_units_ago = one_spark_unit_ago - timedelta(days=18)
    three_spark_units_ago = two_spark_units_ago - timedelta(days=18)
    four_spark_units_ago = three_spark_units_ago - timedelta(days=18)
    five_spark_units_ago = four_spark_units_ago - timedelta(days=18)

    #6mo
    one_6mo_unit_ago = today - timedelta(days=45)
    two_6mo_units_ago = one_6mo_unit_ago - timedelta(days=45)
    three_6mo_units_ago = two_6mo_units_ago - timedelta(days=45)
    four_6mo_units_ago = three_6mo_units_ago - timedelta(days=45)

    #12mo
    one_12mo_unit_ago = today - timedelta(days=92)
    two_12mo_units_ago = one_12mo_unit_ago - timedelta(days=92)
    three_12mo_units_ago = two_12mo_units_ago - timedelta(days=92)
    four_12mo_units_ago = three_12mo_units_ago - timedelta(days=92)

    #24mo
    one_24mo_unit_ago = today - timedelta(days=183)
    two_24mo_units_ago = one_24mo_unit_ago - timedelta(days=183)
    three_24mo_units_ago = two_24mo_units_ago - timedelta(days=183)
    four_24mo_units_ago = three_24mo_units_ago - timedelta(days=183)


    publish_datetime = datetime(publish_date.year, publish_date.month, publish_date.day)
    #epoch = datetime.datetime.utcfromtimestamp(0)
    epoch = datetime(1970, 1, 1)
    publish_since_epoch = (publish_datetime - epoch).total_seconds() * 1000

    ylpline_ratings.append([publish_since_epoch, smooth_rating])
    review_ratings.append([publish_since_epoch, actual_rating])
    # g_data = {review.id: (review.publish_date, actual_rating, smooth_rating)}
    prev_smooth_rating = smooth_rating


    one_spark_unit_back = []
    two_spark_units_back = []
    three_spark_units_back = []
    four_spark_units_back = []
    five_spark_units_back = []

    one_6mo_unit_back = []
    two_6mo_units_back = []
    three_6mo_units_back = []
    four_6mo_units_back = []

    one_12mo_unit_back = []
    two_12mo_units_back = []
    three_12mo_units_back = []
    four_12mo_units_back = []

    one_24mo_unit_back = []
    two_24mo_units_back = []
    three_24mo_units_back = []
    four_24mo_units_back = []

    #print(str(one_12mo_unit_ago))
    #print(str(two_12mo_units_ago))
    #print(str(three_12mo_units_ago))
    #print(str(four_12mo_units_ago))
    #print(str(five_6mo_units_ago))
    for review in reviews[1:]:
        publish_date = review.publish_date
        publish_datetime = datetime(publish_date.year, publish_date.month, publish_date.day)
        publish_since_epoch = (publish_datetime - epoch).total_seconds() * 1000

        actual_rating = float(review.rating)
        smooth_rating = float(prev_smooth_rating + SMOOTH_FACTOR * (actual_rating-prev_smooth_rating))
        #print(str(publish_date))

        if publish_date > one_spark_unit_ago:
            #print("one")
            one_spark_unit_back.append(smooth_rating)
        elif publish_date > two_spark_units_ago:
            #print("two")
            two_spark_units_back.append(smooth_rating)
        elif publish_date > three_spark_units_ago:
            #print("three")
            three_spark_units_back.append(smooth_rating)
        elif publish_date > four_spark_units_ago:
            #print("four")
            four_spark_units_back.append(smooth_rating)
        elif publish_date > five_spark_units_ago:
            #print("five")
            five_spark_units_back.append(smooth_rating)

        if publish_date > one_6mo_unit_ago:
            one_6mo_unit_back.append(smooth_rating)
        elif publish_date > two_6mo_units_ago:
            two_6mo_units_back.append(smooth_rating)
        elif publish_date > three_6mo_units_ago:
            three_6mo_units_back.append(smooth_rating)
        elif publish_date > four_6mo_units_ago:
            four_6mo_units_back.append(smooth_rating)

        if publish_date > one_12mo_unit_ago:
            one_12mo_unit_back.append(smooth_rating)
        elif publish_date > two_12mo_units_ago:
            two_12mo_units_back.append(smooth_rating)
        elif publish_date > three_12mo_units_ago:
            three_12mo_units_back.append(smooth_rating)
        elif publish_date > four_12mo_units_ago:
            four_12mo_units_back.append(smooth_rating)

        if publish_date > one_24mo_unit_ago:
            one_24mo_unit_back.append(smooth_rating)
        elif publish_date > two_24mo_units_ago:
            two_24mo_units_back.append(smooth_rating)
        elif publish_date > three_24mo_units_ago:
            three_24mo_units_back.append(smooth_rating)
        elif publish_date > four_24mo_units_ago:
            four_24mo_units_back.append(smooth_rating)

        #g_data[review.id] = (review.publish_date, actual_rating, smooth_rating)
        ylpline_ratings.append([publish_since_epoch, smooth_rating])
        review_ratings.append([publish_since_epoch, actual_rating])

        prev_smooth_rating = smooth_rating

    #series_data = [{'name': 'ylpline rating', 'data': ylpline_ratings},
    #              {'name': 'review rating', 'data': review_ratings}]
    sparkline = get_sparkline([five_spark_units_back, four_spark_units_back, three_spark_units_back, two_spark_units_back, one_spark_unit_back])
    sparkline_6mo = get_sparkline([four_6mo_units_back, three_6mo_units_back, two_6mo_units_back, one_6mo_unit_back])
    sparkline_12mo = get_sparkline([four_12mo_units_back, three_12mo_units_back, two_12mo_units_back, one_12mo_unit_back])
    sparkline_24mo = get_sparkline([four_24mo_units_back, three_24mo_units_back, two_24mo_units_back, one_24mo_unit_back])

    print(str(sparkline))
    print(str(sparkline_6mo))
    print(str(sparkline_12mo))
    print(str(sparkline_24mo))
    #print(str(ylpline_ratings))
    #print(str(sorted(g_data.items())))
    return (ylpline_ratings, review_ratings, smooth_rating, sparkline, sparkline_6mo, sparkline_12mo, sparkline_24mo)


def get_sparkline(ratings):
    sparkline = []
    #print(str(ratings))
    for week in ratings:
        rating_count = len(week)
        rating_sum = 0

        for rating in week:
            rating_sum += rating;

        if rating_count > 0:
            sparkline.append(round(float(rating_sum)/float(rating_count), 2))

    return sparkline

