# -*- coding: utf-8 -*-
from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page', on_delete=models.CASCADE)),
                ('link_url', cms.models.fields.LinkField(help_text=b'The URL where the user will be redirected.', max_length=1000, verbose_name=b'link URL')),
                ('new_window', models.BooleanField(default=False, help_text=b'Open the page in a new window.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
