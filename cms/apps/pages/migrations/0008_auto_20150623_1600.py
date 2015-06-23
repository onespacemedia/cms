# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_remove_page_meta_keywords'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='og_description',
            field=models.TextField(help_text='Description that will appear ont he Facebook post, it is limited to 300characters but is recommended not to use anything over 200.', max_length=300, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='og_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91/1 ratio) this gives you a bigstand out thumbnail. Using an image smaller than 400x209 will give you a verysmall thumbnail and splits your post into 2 columns.If you have text on the image make sure it is centered as Facebook crops imagesto get the text centered so you may lose some of your image.', null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='page',
            name='og_title',
            field=models.CharField(help_text='Title that will appear on the Facebook post, it is limited to 100 charactersbecause Facebook truncates the title to 88 characters.', max_length=100, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='twitter_card',
            field=models.CharField(default='summary', help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', max_length=100, verbose_name='card', choices=[('summary', 'Summary'), ('photo', 'Photo'), ('video', 'Video'), ('product', 'Product'), ('app', 'App'), ('gallery', 'Gallery'), ('large-summary', 'Large Summary')]),
        ),
        migrations.AlterField(
            model_name='page',
            name='twitter_description',
            field=models.TextField(help_text="Description that will appear on the Twitter card, it is limited to 200 charactersYou don't need to focus on keywords as this does'nt effect SEO so focus oncopy that compliments the tweet and title.", max_length=200, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='twitter_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150, if you want to use a larger imagemake sure the card type is set to "Large Summary"', null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='page',
            name='twitter_title',
            field=models.CharField(help_text='The title that appears on the Twitter card, it is limited to 70 characters.', max_length=70, verbose_name='title', blank=True),
        ),
    ]
