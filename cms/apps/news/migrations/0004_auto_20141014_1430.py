# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_article_approved'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='approved',
        ),
        migrations.AddField(
            model_name='article',
            name='status',
            field=models.CharField(default=b'draft', max_length=100, choices=[(b'draft', b'Draft'), (b'submitted', b'Submitted for approval'), (b'approved', b'Approved')]),
            preserve_default=True,
        ),
    ]
