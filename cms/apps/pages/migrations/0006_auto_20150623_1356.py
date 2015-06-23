# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_auto_20150623_1128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='twitter_card',
            field=models.CharField(default='summary', help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', max_length=100, choices=[('summary', 'Summary'), ('photo', 'Photo'), ('video', 'Video'), ('product', 'Product'), ('app', 'App'), ('gallery', 'Gallery'), ('large-summary', 'Large Summary')]),
        ),
    ]
