# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20160326_2033'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='latest_review_pull',
            field=models.DateField(blank=True, null=True),
        ),
    ]
