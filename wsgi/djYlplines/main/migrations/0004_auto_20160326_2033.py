# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160326_1820'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='business_id',
            new_name='business',
        ),
    ]
