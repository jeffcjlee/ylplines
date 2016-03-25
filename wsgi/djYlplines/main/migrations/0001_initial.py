# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('image_url', models.URLField()),
                ('url', models.URLField()),
                ('review_count', models.PositiveIntegerField()),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('rating', models.DecimalField(decimal_places=1, max_digits=2)),
                ('publish_date', models.DateField()),
                ('business_id', models.ForeignKey(to='main.Business')),
            ],
        ),
    ]
