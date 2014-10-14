# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_auto_20141014_1434'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='high_resolution_mp4',
            field=cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'high resolution MP4', blank=True, to='media.File', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='video',
            name='low_resolution_mp4',
            field=cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'low resolution MP4', blank=True, to='media.File', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='video',
            name='webm',
            field=cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'WebM', blank=True, to='media.File', null=True),
            preserve_default=True,
        ),
    ]
