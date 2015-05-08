# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0008_page_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countrygroup',
            name='countries',
        ),
        migrations.AddField(
            model_name='country',
            name='group',
            field=models.ForeignKey(blank=True, to='pages.CountryGroup', null=True),
        ),
    ]
