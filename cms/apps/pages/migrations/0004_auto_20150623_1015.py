# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def transfer_url_titles(apps, schema_editor):
    Page = apps.get_model('pages', 'Page')

    for page in Page.objects.all():
        url_title = page.url_title
        page.slug = url_title
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_page_hide_from_anonymous'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='slug',
            field=models.SlugField(help_text='A user friendly URL', null=True),
            preserve_default=False,
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
    ]
