# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0002_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('entry', models.DateField(blank=True)),
                ('exit', models.DateField(blank=True)),
                ('group', models.ForeignKey(to='sigma_core.Group', related_name='memberships')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='memberships')),
            ],
        ),
    ]
