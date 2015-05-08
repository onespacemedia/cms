# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20150506_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='country_group',
            field=models.ForeignKey(verbose_name='Target country group', to='pages.CountryGroup'),
        ),
    ]
