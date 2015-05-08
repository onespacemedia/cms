# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_auto_20150507_1027'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_content_object',
            field=models.BooleanField(default=False),
        ),
    ]
