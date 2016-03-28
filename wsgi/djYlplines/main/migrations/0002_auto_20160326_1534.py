# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='business',
            name='id',
            field=models.CharField(unique=True, serialize=False, max_length=200, primary_key=True),
        ),
        migrations.AlterField(
            model_name='business',
            name='image_url',
            field=models.URLField(max_length=500),
        ),
        migrations.AlterField(
            model_name='business',
            name='url',
            field=models.URLField(max_length=500),
        ),
    ]
