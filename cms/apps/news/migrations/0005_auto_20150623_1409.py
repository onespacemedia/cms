# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20150623_1356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='meta_keywords',
        ),
        migrations.RemoveField(
            model_name='category',
            name='meta_keywords',
        ),
    ]
