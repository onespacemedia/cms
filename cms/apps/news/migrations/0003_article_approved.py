# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20140909_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='approved',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
