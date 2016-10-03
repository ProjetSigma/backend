# -*- coding: utf-8 -*-
from django.db import models

from sigma_chat.models.chat import Chat


class ChatMember(models.Model):
    is_creator = models.BooleanField()
    is_admin = models.BooleanField()
    is_member = models.BooleanField(default=True)
    is_banned = models.BooleanField(default=False)
    user = models.ForeignKey('sigma_core.User', related_name='user_chatmember')
    chat = models.ForeignKey(Chat, related_name='chatmember')
    
    # Related fields : 
    #     - member_message (model Message.member)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        # Return True if user is the one of this ChatMember or if user is admin on the related chat
        return request.user.is_chat_member(self.chat)

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        # Return True if user is the one of this ChatMember or if user is admin on the related chat
        return (not self.is_creator) and (request.user == self.user or request.user.is_chat_admin(self.chat))
