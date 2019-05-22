# -*- coding: utf-8 -*-
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
            field=models.PositiveSmallIntegerField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='file',
            name='width',
            field=models.PositiveSmallIntegerField(null=True, blank=True, default=0),
        ),
    ]
