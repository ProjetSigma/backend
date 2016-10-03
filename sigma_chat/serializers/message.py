# -*- coding: utf-8 -*-
from rest_framework import serializers

from sigma_chat.models.chat import Chat
from sigma_chat.models.message import Message
from sigma_core.models.user import User
from rest_framework.serializers import ValidationError

import requests
import json

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

    ################################################################
    # CHAT                                                         #
    ################################################################

    def save(self, *args, **kwargs):
        super(MessageSerializer, self).save(*args, **kwargs)
        """
        NO_PROXY = {
            'no': 'pass',
        }
        message = {'message': json.dumps({
                    'chat':{'id': self.data['chat_id']},
                    'chatmember':{'id': self.data['chatmember_id']},
                    'text': self.data['text'],
                    'attachment': self.data['attachment'],
                    'date': self.data['date']
                })
            }
        requests.post('http://localhost:8000/tornado/chat/?secret_key=', data=message, proxies=NO_PROXY)
        """
