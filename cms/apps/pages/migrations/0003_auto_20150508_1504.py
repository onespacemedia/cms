# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20150508_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='country_group',
            field=models.ForeignKey(blank=True, to='pages.CountryGroup', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('parent', 'url_title', 'country_group')]),
        ),
    ]
