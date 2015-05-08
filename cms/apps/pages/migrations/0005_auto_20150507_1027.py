# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20150506_1453'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('parent', 'url_title')]),
        ),
        migrations.RemoveField(
            model_name='page',
            name='country_group',
        ),
    ]
