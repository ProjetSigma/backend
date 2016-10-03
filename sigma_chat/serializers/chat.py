# -*- coding: utf-8 -*-
from rest_framework import serializers

from sigma_chat.models.chat import Chat
from sigma_chat.models.chat_member import ChatMember
from sigma_core.models.user import User

class ChatSerializer(serializers.ModelSerializer):
    """
    Serialize ChatMember model.
    """
    class Meta:
        model = Chat

    def create(self, data):
        chat = Chat(**data)
        if 'user' in self.initial_data:
            try:
                user = User.objects.get(pk=self.initial_data['user'])
                chat.save()
                creator = ChatMember(user=user, is_creator=True, is_admin=True, chat=chat)
                creator.save()
                chat.chatmember.add(creator)
                chat.save()
                return chat
            except User.DoesNotExist:
                return None
        return None
