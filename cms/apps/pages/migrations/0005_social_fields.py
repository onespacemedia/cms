# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
        ('pages', '0004_url_title_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='meta_keywords',
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
            name='twitter_card',
            field=models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', null=True, verbose_name='card'),
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
        migrations.AlterField(
            model_name='page',
            name='hide_from_anonymous',
            field=models.BooleanField(default=False, help_text="Visitors that aren't logged in won't see this page in the navigation", verbose_name='show to logged in only'),
        ),
        migrations.AlterField(
            model_name='page',
            name='requires_authentication',
            field=models.BooleanField(default=False, help_text='Visitors will need to be logged in to see this page'),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(help_text='A user friendly URL'),
        ),
    ]
