# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20150623_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='twitter_card',
        ),
        migrations.RemoveField(
            model_name='category',
            name='twitter_card',
        ),
    ]
