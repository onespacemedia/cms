# Generated by Django 2.2.18 on 2021-03-26 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_auto_20201009_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='browser_title',
            field=models.CharField(blank=True, help_text='The title that appears in search results. Use 50-60 characters and include relevant keywords.', max_length=1000, verbose_name='Title tag'),
        ),
        migrations.AlterField(
            model_name='page',
            name='meta_description',
            field=models.TextField(blank=True, help_text='A concise and compelling description of the contents of the page. Use 50-160 characters and include relevant keywords.'),
        ),
    ]
