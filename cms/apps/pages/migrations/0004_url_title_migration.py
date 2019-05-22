# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_page_hide_from_anonymous'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='url_title',
            new_name='slug',
        ),
    ]
