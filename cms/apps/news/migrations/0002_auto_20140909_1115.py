# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.apps.news.models
import cms.apps.media.models
from django.conf import settings
import django.db.models.deletion
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
        ('pages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsFeed',
            fields=[
                ('page', models.OneToOneField(related_name=b'+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
                ('content_primary', cms.models.fields.HtmlField(verbose_name=b'primary content', blank=True)),
                ('per_page', models.IntegerField(default=5, null=True, verbose_name=b'articles per page', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('url_title',)]),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(to='news.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='image',
            field=cms.apps.media.models.ImageRefField(related_name=b'+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='news_feed',
            field=models.ForeignKey(default=cms.apps.news.models.get_default_news_feed, to='news.NewsFeed'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('news_feed', 'date', 'url_title')]),
        ),
    ]
