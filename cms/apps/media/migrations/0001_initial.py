# -*- coding: utf-8 -*-
from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(help_text='The title will be used as the default rollover text when this media is embedded in a web page.', max_length=200)),
                ('file', models.FileField(max_length=250, upload_to='uploads/files')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('high_resolution_mp4', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='high resolution MP4', blank=True, to='media.File', null=True)),
                ('image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', null=True)),
                ('low_resolution_mp4', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='low resolution MP4', blank=True, to='media.File', null=True)),
                ('webm', cms.apps.media.models.VideoFileRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, verbose_name='WebM', blank=True, to='media.File', null=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AddField(
            model_name='file',
            name='labels',
            field=models.ManyToManyField(help_text='Labels are used to help organise your media. They are not visible to users on your website.', to='media.Label', blank=True),
        ),
    ]
