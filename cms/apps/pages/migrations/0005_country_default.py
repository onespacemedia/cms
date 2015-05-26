# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20150519_1700'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='default',
            field=models.NullBooleanField(default=None, unique=True),
        ),
    ]
