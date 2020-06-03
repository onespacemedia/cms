# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0003_file_alt_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='file',
            field=models.FileField(storage=cms.apps.media.models.MediaStorage(), max_length=250, upload_to='uploads/files'),
        ),
    ]
