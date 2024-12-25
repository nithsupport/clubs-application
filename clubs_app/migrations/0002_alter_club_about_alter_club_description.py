# Generated by Django 5.0.2 on 2024-02-09 13:31

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clubs_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='club',
            name='about',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='club',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]