# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0002_auto_20150713_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='alt_text',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
