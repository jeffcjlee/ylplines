from django.db import models

# Create your models here.


class Business(models.Model):
    name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=200)
    url = models.URLField(max_length=200)
    review_count = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)


class Review(models.Model):
    business_id = models.ForeignKey(Business)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    publish_date = models.DateField()
