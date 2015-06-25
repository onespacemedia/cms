# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.apps.media.models
import django.db.models.deletion


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# cms.apps.pages.migrations.0004_auto_20150623_1015


def transfer_url_titles(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')

    for page in Page.objects.all():
        url_title = page.url_title
        page.slug = url_title
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=16)),
                ('default', models.NullBooleanField(default=None, unique=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'countries',
            },
        ),
        migrations.CreateModel(
            name='CountryGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text="Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name='online')),
                ('browser_title', models.CharField(help_text="The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_keywords', models.CharField(help_text='A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.', max_length=1000, verbose_name='keywords', blank=True)),
                ('meta_description', models.TextField(help_text='A brief description of the contents of this page.', verbose_name='description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, 'Very high'), (0.8, 'High'), (0.5, 'Medium'), (0.3, 'Low'), (0.0, 'Very low')], blank=True, help_text='The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name='priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, 'Always'), (2, 'Hourly'), (3, 'Daily'), (4, 'Weekly'), (5, 'Monthly'), (6, 'Yearly'), (7, 'Never')], blank=True, help_text='How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name='change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text='Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name='allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text='Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name='follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text='Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name='allow archiving')),
                ('url_title', models.SlugField(verbose_name='URL title')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text='A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('left', models.IntegerField(editable=False, db_index=True)),
                ('right', models.IntegerField(editable=False, db_index=True)),
                ('is_content_object', models.BooleanField(default=False)),
                ('publication_date', models.DateTimeField(help_text='The date that this page will appear on the website.  Leave this blank to immediately publish this page.', null=True, db_index=True, blank=True)),
                ('expiry_date', models.DateTimeField(help_text='The date that this page will be removed from the website.  Leave this blank to never expire this page.', null=True, db_index=True, blank=True)),
                ('in_navigation', models.BooleanField(default=True, help_text='Uncheck this box to remove this content from the site navigation.', verbose_name='add to navigation')),
                ('cached_url', models.CharField(max_length=1000, null=True, blank=True)),
                ('content_type', models.ForeignKey(editable=False, to='contenttypes.ContentType', help_text='The type of page content.')),
                ('country_group', models.ForeignKey(blank=True, to='pages.CountryGroup', null=True)),
                ('owner', models.ForeignKey(related_name='owner_set', blank=True, to='pages.Page', null=True)),
                ('parent', models.ForeignKey(related_name='child_set', blank=True, to='pages.Page', null=True)),
            ],
            options={
                'ordering': ('left',),
            },
        ),
        migrations.AddField(
            model_name='country',
            name='group',
            field=models.ForeignKey(blank=True, to='pages.CountryGroup', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('parent', 'url_title', 'country_group')]),
        ),
        migrations.AddField(
            model_name='page',
            name='requires_authentication',
            field=models.BooleanField(default=False, help_text='Visitors will need to be logged in to see this page'),
        ),
        migrations.AddField(
            model_name='page',
            name='hide_from_anonymous',
            field=models.BooleanField(default=False, help_text="Visitors that aren't logged in won't see this page in the navigation", verbose_name='show to logged in only'),
        ),
        migrations.AddField(
            model_name='page',
            name='slug',
            field=models.SlugField(help_text='A user friendly URL', null=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('parent', 'slug', 'country_group')]),
        ),
        migrations.RunPython(transfer_url_titles),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(help_text='A user friendly URL'),
        ),
        migrations.RemoveField(
            model_name='page',
            name='url_title',
        ),
        migrations.AddField(
            model_name='page',
            name='og_description',
            field=models.TextField(help_text='Description that will appear ont he Facebook post, it is limited to 300characters but is recommended not to use anything over 200.', max_length=300, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='og_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91/1 ratio) this gives you a bigstand out thumbnail. Using an image smaller than 400x209 will give you a verysmall thumbnail and splits your post into 2 columns.If you have text on the image make sure it is centered as Facebook crops imagesto get the text centered so you may lose some of your image.', null=True, verbose_name='image'),
        ),
        migrations.AddField(
            model_name='page',
            name='og_title',
            field=models.CharField(help_text='Title that will appear on the Facebook post, it is limited to 100 charactersbecause Facebook truncates the title to 88 characters.', max_length=100, verbose_name='title', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='twitter_description',
            field=models.TextField(help_text="Description that will appear on the Twitter card, it is limited to 200 charactersYou don't need to focus on keywords as this does'nt effect SEO so focus oncopy that compliments the tweet and title.", max_length=200, verbose_name='description', blank=True),
        ),
        migrations.AddField(
            model_name='page',
            name='twitter_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150, if you want to use a larger imagemake sure the card type is set to "Large Summary"', null=True, verbose_name='image'),
        ),
        migrations.AddField(
            model_name='page',
            name='twitter_title',
            field=models.CharField(help_text='The title that appears on the Twitter card, it is limited to 70 characters.', max_length=70, verbose_name='title', blank=True),
        ),
        migrations.RemoveField(
            model_name='page',
            name='meta_keywords',
        ),
        migrations.AddField(
            model_name='page',
            name='twitter_card',
            field=models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', null=True, verbose_name='card'),
        ),
    ]
