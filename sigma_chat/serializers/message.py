# -*- coding: utf-8 -*-
from rest_framework import serializers

from sigma_chat.models.message import Message
from rest_framework.serializers import ValidationError

class MessageSerializer(serializers.ModelSerializer):
    """
    Serialize Message model.
    """
    class Meta:
        model = Message

    def validate(self, data):
        if "chatmember_id" not in data:
            raise ValidationError("No user given.")
        if "chat_id" not in data:
            raise ValidationError("No chat given.")
        if data['chat_id'].id != data['chatmember_id'].chat.id:
            raise ValidationError("ChatMember not allowed to publish on this chat.")
        if data['text'] is None and data['attachment'] is None:
            raise ValidationError("You must send either a text or a file.")

        return data
