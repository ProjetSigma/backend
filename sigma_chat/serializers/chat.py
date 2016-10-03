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
