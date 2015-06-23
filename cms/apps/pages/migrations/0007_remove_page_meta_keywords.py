# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_auto_20150623_1356'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='meta_keywords',
        ),
    ]
