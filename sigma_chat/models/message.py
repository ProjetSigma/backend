# -*- coding: utf-8 -*-
from django.db import models

from sigma_chat.models.chat_member import ChatMember
from sigma_chat.models.chat import Chat


def chat_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/chats/{0}/{1}'.format(instance.chat.id, filename)


class Message(models.Model):
    text = models.TextField(blank=True)
    chatmember_id = models.ForeignKey(ChatMember, related_name='chatmember_message')
    chat_id = models.ForeignKey(Chat, related_name='message')
    date = models.DateTimeField(auto_now=True)
    attachment = models.FileField(upload_to=chat_directory_path, blank=True)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return request.user.is_member(self.chat)

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        return request.user == self.chatmember.user and self.chatmember.is_member
