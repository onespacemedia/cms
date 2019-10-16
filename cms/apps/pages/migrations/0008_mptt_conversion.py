# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-10-15 15:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields

def forwards_page_tree_level(apps, schema_editor):
    def set_page_child_levels(page, level):
        page.level = level
        page.save()

        for child in page.child_set.all():
            set_page_child_levels(child, level + 1)

    Page = apps.get_model('pages', 'Page')
    db_alias = schema_editor.connection.alias

    homepage = Page.objects.using(db_alias).filter(parent=None).first()
    set_page_child_levels(homepage, 0)

def reverse_page_tree_level(apps, schema_editor):
    # We don't have anything here are we're removing the 'level' field anyway
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_remove_page_cached_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='level',
            field=models.PositiveIntegerField(default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=0, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='page',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_set', to='pages.Page'),
        ),
        migrations.RunPython(forwards_page_tree_level, reverse_page_tree_level),
    ]
