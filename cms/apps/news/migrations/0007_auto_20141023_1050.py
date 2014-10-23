# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_auto_20141014_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.CharField(default=b'draft', max_length=100, choices=[(b'draft', b'Draft'), (b'submitted', b'Submitted for approval'), (b'approved', b'Approved')]),
            preserve_default=True,
        ),
    ]
