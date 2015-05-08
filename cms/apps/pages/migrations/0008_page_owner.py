# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_page_country_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='owner',
            field=models.ForeignKey(related_name='owner_set', blank=True, to='pages.Page', null=True),
        ),
    ]
