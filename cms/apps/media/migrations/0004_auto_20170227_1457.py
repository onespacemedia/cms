# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_file_alt_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='external_url',
            field=models.URLField(help_text='Use this for externally-hosted videos, e.g. YouTube.', null=True, verbose_name='external URL', blank=True),
        ),
        migrations.AddField(
            model_name='video',
            name='iframe_url',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
