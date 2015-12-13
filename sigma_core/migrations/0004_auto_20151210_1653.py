# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0003_usergroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroup',
            name='entry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='usergroup',
            name='exit',
            field=models.DateField(blank=True, null=True),
        ),
    ]
