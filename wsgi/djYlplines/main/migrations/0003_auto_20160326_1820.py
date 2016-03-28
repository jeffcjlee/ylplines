# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20160326_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='id',
            field=models.CharField(max_length=200, unique=True, serialize=False, primary_key=True),
        ),
    ]
