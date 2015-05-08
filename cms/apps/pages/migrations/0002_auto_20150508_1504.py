# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('code', models.CharField(max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='CountryGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='page',
            name='is_content_object',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='page',
            name='owner',
            field=models.ForeignKey(related_name='owner_set', blank=True, to='pages.Page', null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='group',
            field=models.ForeignKey(blank=True, to='pages.CountryGroup', null=True),
        ),
    ]
