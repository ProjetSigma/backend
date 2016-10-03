# -*- coding: utf-8 -*-
from django.db import models


class Chat(models.Model):
    name = models.CharField(max_length=50)
    
    # Related fields : 
    #     - chatmember (model ChatMember.chat)
    #     - message (model Message.chat)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return request.user.is_chat_member(self)

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        return request.user.is_chat_admin(self)
        
