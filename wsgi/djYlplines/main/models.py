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
from django.db import models

# Create your models here.


class Business(models.Model):
    id = models.CharField(max_length=200, primary_key=True, unique=True)
    name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    url = models.URLField(max_length=500)
    review_count = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    latest_review_pull = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    id = models.CharField(max_length=200, primary_key=True, unique=True)
    business = models.ForeignKey(Business)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    publish_date = models.DateField()
    text = models.TextField(default="")

    def __str__(self):
        return "Review published on %s with a rating of %s" % self.publish_date, self.rating
