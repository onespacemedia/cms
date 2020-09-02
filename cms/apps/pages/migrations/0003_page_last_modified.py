# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20160414_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='last_modified',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
