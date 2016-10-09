from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory

from sigma_chat.tests.factories import ChatFactory, ChatMemberFactory

from sigma_chat.models.chat import Chat
from sigma_chat.serializers.chat import ChatSerializer


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class ChatTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        # Summary: 4 users + 1 admin, 1 chat
        # User #5 is Sigma admin
        # User #1 is in chat

        super(ChatTests, self).setUpTestData()
        self.users = UserFactory.create_batch(3) + [AdminUserFactory()]
        self.chats = ChatFactory.create_batch(1)
        self.chatmember = ChatMemberFactory(is_creator=True, is_admin=True, chat=self.chats[0], user=self.users[0])

        self.chats_url = "/chat/"
        self.chat_url = self.chats_url + "%d/"

        self.new_chat_data = {"name": "New chat"}
        self.add_member_data = {"user_id": self.users[0].id}

#### Model methods test
    def test_model_chat(self):
        self.assertEqual(len(self.chats), 1)
        self.assertEqual(len(self.chats[0].chatmember.all()), 1)
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_creator)
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_admin)
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_member)
        self.assertFalse(self.chats[0].chatmember.get(pk=1).is_banned)

#### List requests
    def test_get_chats_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.chats_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_chats_list_limited(self):
        # Client authenticated and can see limited list of chats
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.chats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_chats_list_creator(self):
        # Client authenticated and can see limited list of chats
        self.client.force_authenticate(user=self.chats[0].chatmember.get(pk=1).user)
        response = self.client.get(self.chats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_chats_list_admin(self):
        # Client authenticated and can see limited list of chats
        self.client.force_authenticate(user=self.users[-1])
        response = self.client.get(self.chats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

#### Get requests
    def test_get_chat_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.chat_url % self.chats[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_chat_creator(self):
        # Client can see chat
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.chat_url % self.chats[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_chat_not_member(self):
        # Client cannot see chat if he's not a member
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.chat_url % self.chats[0].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#### Create requests
    def test_create_unauthed(self):
        # Client is not authenticated
        response = self.client.post(self.chats_url, self.new_chat_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_chat(self):
        # Everybody can create a chat
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.chats_url, self.new_chat_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.new_chat_data['name'])
        Chat.objects.get(pk=response.data['id']).delete()

#### Modification requests
    def test_update_unauthed(self):
        # Unauthed client cannot update a chat
        update_chat_data = ChatSerializer(self.chats[0]).data
        response = self.client.put(self.chat_url % self.chats[0].id, update_chat_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_forbidden(self):
        # Client cannot update a chat if he isn't admin of
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.chat_url % self.chats[0].id, {'name': "new name"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ok(self):
        # Client can update a chat if he has clearance
        update_chat_data = ChatSerializer(self.chats[0]).data
        self.client.force_authenticate(user=self.users[0])
        old_name = update_chat_data['name']
        update_chat_data['name'] = "A new name"
        response = self.client.put(self.chat_url % self.chats[0].id, update_chat_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reload(self.chats[0]).name, update_chat_data['name'])
        # Guarantee independance of tests
        self.chats[0].name = old_name
        self.chats[0].save()
