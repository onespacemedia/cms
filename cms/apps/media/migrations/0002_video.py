# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('high_resolution_mp4', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'high resolution MP4', blank=True, to='media.File', null=True)),
                ('image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', null=True)),
                ('low_resolution_mp4', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'low resolution MP4', blank=True, to='media.File', null=True)),
                ('webm', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name=b'WebM', blank=True, to='media.File', null=True)),
            ],
            options={
                'ordering': ('title',),
            },
            bases=(models.Model,),
        ),
    ]
