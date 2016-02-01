# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-08 16:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sigma_core', '0007_auto_20160102_1647'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='membership_policy',
        ),
        migrations.RemoveField(
            model_name='group',
            name='validation_policy',
        ),
        migrations.AddField(
            model_name='group',
            name='default_member_rank',
            field=models.SmallIntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_accept_join_requests',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_demote',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_invite',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_kick',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_modify_group_infos',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='group',
            name='req_rank_promote',
            field=models.SmallIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='user',
            name='invited_to_groups',
            field=models.ManyToManyField(related_name='invited_users', to='sigma_core.Group'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='perm_rank',
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='usergroup',
            unique_together=set([('user', 'group')]),
        ),
    ]