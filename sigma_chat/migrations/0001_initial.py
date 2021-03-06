# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-04 09:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sigma_chat.models.message


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ChatMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_creator', models.BooleanField()),
                ('is_admin', models.BooleanField()),
                ('is_member', models.BooleanField(default=True)),
                ('is_banned', models.BooleanField(default=False)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatmember', to='sigma_chat.Chat')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_chatmember', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('attachment', models.FileField(blank=True, upload_to=sigma_chat.models.message.chat_directory_path)),
                ('chat_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message', to='sigma_chat.Chat')),
                ('chatmember_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chatmember_message', to='sigma_chat.ChatMember')),
            ],
        ),
    ]
