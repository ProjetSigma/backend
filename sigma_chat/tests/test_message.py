from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory

from sigma_chat.tests.factories import ChatFactory, ChatMemberFactory, MessageFactory

from sigma_chat.models.message import Message


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class MessageTests(APITestCase):
    def setUp(self):
        # Summary: 4 users + 1 admin, 2 chats
        # User #5 is Sigma admin
        # User #1 is creator of and sent 1 message to chat #1, User #3 is member of, and sent 1 message to chat#1
        # User #2 is creator of, and sent 1 message to chat #2, User #1 is member of, and sent 1 message to chat #2

        super(MessageTests, self).setUp()
        self.users = UserFactory.create_batch(4) + [AdminUserFactory()]
        self.chats = ChatFactory.create_batch(2)
        self.chatmembers = [
            ChatMemberFactory(is_creator=True, is_admin=True, chat=self.chats[0], user=self.users[0]),
            ChatMemberFactory(is_creator=False, is_admin=False, chat=self.chats[1], user=self.users[0]),
            ChatMemberFactory(is_creator=True, is_admin=True, chat=self.chats[1], user=self.users[1]),
            ChatMemberFactory(is_creator=False, is_admin=False, chat=self.chats[0], user=self.users[2])
        ]
        self.messages = [
            MessageFactory(chat_id=self.chats[0], chatmember_id=self.chatmembers[0]),
            MessageFactory(chat_id=self.chats[1], chatmember_id=self.chatmembers[1]),
            MessageFactory(chat_id=self.chats[1], chatmember_id=self.chatmembers[2]),
            MessageFactory(chat_id=self.chats[0], chatmember_id=self.chatmembers[3]),
        ]

        self.messages_url = "/message/"
        self.message_url = self.messages_url + "%d/"
        self.create_message_url = "/chatmember/{0}/send_message/"

        f = SimpleUploadedFile("file.txt", b"file_content")
        self.new_message_data = {"chatmember_id": self.chatmembers[0].id, "chat_id": self.chats[0].id, "text": "text", 'attachment': f}
        self.new_message_data_right_way = {"text": "text", "attachment": f}


#### Model methods test
    def test_model_message(self):
        self.assertEqual(len(self.messages), 4)
        self.assertEqual(len(self.chats[0].message.all()), 2)
        self.assertEqual(len(self.chats[1].message.all()), 2)
        # Test that user 1 is sender of message 1
        self.assertEqual(self.messages[0].chatmember_id.id,self.chatmembers[0].id)
        self.assertEqual(self.messages[0].chat_id.id, self.chats[0].id)
        # Test that user 1 is sender of message 2
        self.assertEqual(self.messages[1].chatmember_id.id,self.chatmembers[1].id)
        self.assertEqual(self.messages[1].chat_id.id, self.chats[1].id)
        # Test that user 2 is sender of message 3
        self.assertEqual(self.messages[2].chatmember_id.id,self.chatmembers[2].id)
        self.assertEqual(self.messages[2].chat_id.id, self.chats[1].id)
        # Test that user 3 is sender of message 4
        self.assertEqual(self.messages[3].chatmember_id.id,self.chatmembers[3].id)
        self.assertEqual(self.messages[3].chat_id.id, self.chats[0].id)

#### List requests
    def test_get_messages_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_messages_list_limited(self):
        # Client authenticated and can see limited list of messages
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_messages_list_limited2(self):
        # Client authenticated and can see limited list of messages
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_messages_list_limited3(self):
        # Client authenticated and can see limited list of messages
        self.client.force_authenticate(user=self.users[2])
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_messages_list_limited4(self):
        # Client authenticated and can see limited list of messages
        self.client.force_authenticate(user=self.users[3])
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_messages_list_admin(self):
        # Admin authenticated and can see limited list of messages
        self.client.force_authenticate(user=self.users[-1])
        response = self.client.get(self.messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

#### Get requests
    def test_get_message_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.message_url % self.messages[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_message_member(self):
        # Client can see its messages
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.message_url % self.messages[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6) # Message has 6 fields

    def test_get_message_not_member(self):
        # Client cannot see messages if he's not a member of the chat it belongs to
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.message_url % self.messages[0].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#### Create requests
    def test_create_unauthed(self):
        # Client is not authenticated
        response = self.client.post(self.messages_url, self.new_message_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Message.objects.all().count(), len(self.messages))

    # Only members of the chat can create a message for this chat, but on the chatmember's page
    def test_create_message_wrong_way(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.messages_url, self.new_message_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Message.objects.all().count(), len(self.messages))


    def test_create_message_wrong_method(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.create_message_url.format(self.messages[0].id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Message.objects.all().count(), len(self.messages))

    def test_create_message_non_existent_chatmember(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.create_message_url.format(10), self.new_message_data_right_way, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Message.objects.all().count(), len(self.messages))

    def test_create_message_not_self(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.create_message_url.format(self.chatmembers[0].id), self.new_message_data_right_way, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Message.objects.all().count(), len(self.messages))

    def test_create_message_member(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.create_message_url.format(self.chatmembers[0].id), self.new_message_data_right_way, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.all().count(), len(self.messages) + 1)

    def test_create_message_no_content(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.create_message_url.format(self.chatmembers[0].id), {'text':""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.all().count(), len(self.messages))

#### Modification requests
    def test_update_wrong_way(self):
        # Cannot change a message
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.message_url % self.messages[0].id, {'text': "new_text"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(reload(self.messages[0]), self.messages[0])
