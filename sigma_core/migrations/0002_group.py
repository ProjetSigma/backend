# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=254)),
                ('visibility', models.SmallIntegerField(choices=[(0, 'PUBLIC'), (1, 'PRIVATE')], default=1)),
                ('membership_policy', models.SmallIntegerField(choices=[(0, 'ANYONE'), (1, 'REQUEST'), (2, 'INVITATION')], default=2)),
                ('validation_policy', models.SmallIntegerField(choices=[(0, 'ADMINS'), (1, 'MEMBERS')], default=0)),
                ('type', models.SmallIntegerField(choices=[(0, 'BASIC'), (1, 'CURSUS/DEPARTMENT'), (2, 'ASSOCIATION'), (3, 'PROMOTION'), (4, 'SCHOOL')], default=0)),
            ],
        ),
    ]
