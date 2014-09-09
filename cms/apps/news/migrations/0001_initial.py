# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text=b"Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name=b'online')),
                ('browser_title', models.CharField(help_text=b"The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_keywords', models.CharField(help_text=b'A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.', max_length=1000, verbose_name=b'keywords', blank=True)),
                ('meta_description', models.TextField(help_text=b'A brief description of the contents of this page.', verbose_name=b'description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, b'Very high'), (0.8, b'High'), (0.5, b'Medium'), (0.3, b'Low'), (0.0, b'Very low')], blank=True, help_text=b'The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name=b'priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, b'Always'), (2, b'Hourly'), (3, b'Daily'), (4, b'Weekly'), (5, b'Monthly'), (6, b'Yearly'), (7, b'Never')], blank=True, help_text=b'How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name=b'change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name=b'allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name=b'follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name=b'allow archiving')),
                ('url_title', models.SlugField(verbose_name=b'URL title')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text=b'A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('date', models.DateField(default=django.utils.timezone.now, db_index=True)),
                ('content', cms.models.fields.HtmlField(blank=True)),
                ('summary', cms.models.fields.HtmlField(blank=True)),
            ],
            options={
                'ordering': ('-date',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text=b"Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name=b'online')),
                ('browser_title', models.CharField(help_text=b"The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_keywords', models.CharField(help_text=b'A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.', max_length=1000, verbose_name=b'keywords', blank=True)),
                ('meta_description', models.TextField(help_text=b'A brief description of the contents of this page.', verbose_name=b'description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, b'Very high'), (0.8, b'High'), (0.5, b'Medium'), (0.3, b'Low'), (0.0, b'Very low')], blank=True, help_text=b'The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name=b'priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, b'Always'), (2, b'Hourly'), (3, b'Daily'), (4, b'Weekly'), (5, b'Monthly'), (6, b'Yearly'), (7, b'Never')], blank=True, help_text=b'How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name=b'change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name=b'allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name=b'follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name=b'allow archiving')),
                ('url_title', models.SlugField(verbose_name=b'URL title')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text=b'A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('content_primary', cms.models.fields.HtmlField(verbose_name=b'primary content', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
    ]
