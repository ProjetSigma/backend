# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-02 09:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_files', '0001_initial'),
        ('sigma_core', '0016_group_field_group__member_value__validator'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='photo',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sigma_files.Image'),
        ),
    ]