# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-05 16:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0030_auto_20161005_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmember',
            name='is_accepted',
        ),
        migrations.AddField(
            model_name='group',
            name='can_anyone_ask',
            field=models.BooleanField(default=False),
        ),
    ]
