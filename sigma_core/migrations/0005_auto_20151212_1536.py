# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0004_auto_20151210_1653'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usergroup',
            old_name='entry',
            new_name='join_date',
        ),
        migrations.RenameField(
            model_name='usergroup',
            old_name='exit',
            new_name='leave_date',
        ),
    ]
