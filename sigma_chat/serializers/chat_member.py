# -*- coding: utf-8 -*-
from rest_framework import serializers

from sigma_chat.models.chat_member import ChatMember

class ChatMemberSerializer(serializers.ModelSerializer):
    """
    Serialize ChatMember model.
    """
    class Meta:
        model = ChatMember
        exclude = ('user', 'chat')

    user_id = serializers.PrimaryKeyRelatedField(read_only=True, source="user")
    chat_id = serializers.PrimaryKeyRelatedField(read_only=True, source="chat")
    chatmember_message_id = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source="chatmember_message")
