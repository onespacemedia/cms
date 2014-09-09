# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('page', models.OneToOneField(related_name=b'+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
                ('link_url', cms.models.fields.LinkField(help_text=b'The URL where the user will be redirected.', max_length=1000, verbose_name=b'link URL')),
                ('new_window', models.BooleanField(help_text=b'Open the page in a new window.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
