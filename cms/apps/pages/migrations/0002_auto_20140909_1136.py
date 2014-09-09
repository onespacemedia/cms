# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.apps.pages.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=models.ForeignKey(related_name=b'child_set', default=cms.apps.pages.models.get_default_page_parent, blank=True, to='pages.Page', null=True),
        ),
    ]
