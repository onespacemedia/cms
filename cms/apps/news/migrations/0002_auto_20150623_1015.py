# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.SlugField(default='', help_text='A user friendly URL'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default='', help_text='A user friendly URL'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('news_feed', 'date', 'slug')]),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('slug',)]),
        ),
        migrations.RemoveField(
            model_name='article',
            name='url_title',
        ),
        migrations.RemoveField(
            model_name='category',
            name='url_title',
        ),
    ]
