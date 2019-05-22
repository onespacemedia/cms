# -*- coding: utf-8 -*-
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_page_requires_authentication'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='hide_from_anonymous',
            field=models.BooleanField(default=False, help_text="Hide this link from users that aren't logged in"),
        ),
    ]
