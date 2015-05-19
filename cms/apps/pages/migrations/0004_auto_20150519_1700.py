# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150508_1504'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ('name',), 'verbose_name_plural': 'countries'},
        ),
        migrations.AlterModelOptions(
            name='countrygroup',
            options={'ordering': ('name',)},
        ),
        migrations.RemoveField(
            model_name='countrygroup',
            name='default',
        ),
    ]
