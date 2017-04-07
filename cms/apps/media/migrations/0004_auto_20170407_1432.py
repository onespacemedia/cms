# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_file_alt_text'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'ordering': ['title']},
        ),
        migrations.AddField(
            model_name='file',
            name='height',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='file',
            name='width',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
