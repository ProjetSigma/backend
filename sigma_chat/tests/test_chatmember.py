from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory

from sigma_chat.tests.factories import ChatFactory, ChatMemberFactory

from sigma_chat.models.chat_member import ChatMember


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class ChatMemberTests(APITestCase):
    def setUp(self):
        # Summary: 6 users + 1 admin, 2 chats
        # User #7 is Sigma admin
        # User #1 is creator of chat #1, User #3 is member of chat #1, User #4 is admin of chat #1, User #5 has been banned from chat #1, User#6 has left chat #1
        # User #2 is creator of chat #2

        super(ChatMemberTests, self).setUpTestData()
        self.users = UserFactory.create_batch(7) + [AdminUserFactory()]
        self.chats = ChatFactory.create_batch(2)
        self.chatmembers = [
            ChatMemberFactory(is_creator=True, is_admin=True, chat=self.chats[0], user=self.users[0]),
            ChatMemberFactory(is_creator=True, is_admin=True, chat=self.chats[1], user=self.users[1]),
            ChatMemberFactory(is_creator=False, is_admin=False, chat=self.chats[0], user=self.users[2]),
            ChatMemberFactory(is_creator=False, is_admin=True, chat=self.chats[0], user=self.users[3]),
            ChatMemberFactory(is_creator=False, is_admin=False, is_member=False, is_banned=True, chat=self.chats[0], user=self.users[4]),
            ChatMemberFactory(is_creator=False, is_admin=False, is_member=False, chat=self.chats[0], user=self.users[5])
        ]

        self.chatmembers_url = "/chatmember/"
        self.chatmember_url = self.chatmembers_url + "%d/"
        self.create_chatmember_url = "/chat/{0}/add_member/"
        self.change_role_chatmember_url = "/chat/{0}/change_role/"

        self.new_chatmember_data = {"user": self.users[0].id, "chat": self.chats[1].id, "is_creator": False, "is_admin": False}
        self.new_chatmember_data_right_way = {"user_id": self.users[0].id}

        self.new_chatmember_data = {"user": self.users[0].id, "chat": self.chats[1].id, "is_creator": False, "is_admin": False}
        self.new_chatmember_data_right_way = {"user_id": self.users[0].id}


#### Model methods test
    def test_model_chatmember(self):
        self.assertEqual(len(self.chatmembers), 6)
        self.assertEqual(len(self.chats[0].chatmember.all()), 5)
        self.assertEqual(len(self.chats[1].chatmember.all()), 1)
        # Test that user 1 is creator of chat 1
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_creator)
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_admin)
        self.assertTrue(self.chats[0].chatmember.get(pk=1).is_member)
        self.assertFalse(self.chats[0].chatmember.get(pk=1).is_banned)
        # Test that user 2 is creator of chat 2
        self.assertTrue(self.chats[1].chatmember.get(pk=2).is_creator)
        self.assertTrue(self.chats[1].chatmember.get(pk=2).is_admin)
        self.assertTrue(self.chats[1].chatmember.get(pk=2).is_member)
        self.assertFalse(self.chats[1].chatmember.get(pk=2).is_banned)
        # Test that user 2 is only member of chat 2
        self.assertFalse(self.chats[0].chatmember.get(pk=3).is_creator)
        self.assertFalse(self.chats[0].chatmember.get(pk=3).is_admin)
        self.assertTrue(self.chats[0].chatmember.get(pk=3).is_member)
        self.assertFalse(self.chats[0].chatmember.get(pk=3).is_banned)

#### List requests
    def test_get_chatmembers_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_chatmembers_list_limited(self):
        # Client authenticated and can see limited list of chatmembers
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_get_chatmembers_list_limited2(self):
        # Client authenticated and can see limited list of chatmembers
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_chatmembers_list_limited3(self):
        # Client authenticated and can see limited list of chatmembers
        self.client.force_authenticate(user=self.users[2])
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_get_chatmembers_list_limited4(self):
        # Client authenticated and can see limited list of chatmembers
        self.client.force_authenticate(user=self.users[6])
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_get_chatmembers_list_admin(self):
        # Admin authenticated and can see limited list of chatmembers
        self.client.force_authenticate(user=self.users[-1])
        response = self.client.get(self.chatmembers_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

#### Get requests
    def test_get_chatmember_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.chatmember_url % self.chats[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_chatmember_self(self):
        # Client can see its chatmembers
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.chatmember_url % self.chatmembers[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 8) # ChatMember has 8 fields

    def test_get_chatmember_not_self(self):
        # Client cannot see chatmember if he's not a member of the chat it belongs to
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.chatmember_url % self.chats[0].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#### Create requests
    def test_create_unauthed(self):
        # Client is not authenticated
        response = self.client.post(self.chatmembers_url, self.new_chatmember_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    # Only admin on the chat can create a chatmember for this chat, but on the chat's page
    def test_create_chatmember_not_admin_wrong_way(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.chatmembers_url, self.new_chatmember_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_not_member_wrong_way(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.chatmembers_url, self.new_chatmember_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_admin_wrong_way(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.chatmembers_url, self.new_chatmember_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))


    def test_create_chatmember_wrong_method_right_way(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.create_chatmember_url.format(self.chats[1].id))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_non_existent_chat_right_way(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.create_chatmember_url.format(10), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_non_existent_user_right_way(self):
        self.client.force_authenticate(user=self.users[0])
        self.new_chatmember_data_right_way['user_id'] = 10
        response = self.client.post(self.create_chatmember_url.format(self.chats[1].id), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_not_admin_right_way(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.create_chatmember_url.format(self.chats[1].id), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_not_member_right_way(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.create_chatmember_url.format(self.chats[1].id), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_already_member_right_way(self):
        self.client.force_authenticate(user=self.users[1])
        self.new_chatmember_data_right_way['user_id'] = self.users[1].id
        response = self.client.post(self.create_chatmember_url.format(self.chats[1].id), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers))

    def test_create_chatmember_admin_right_way(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.create_chatmember_url.format(self.chats[1].id), self.new_chatmember_data_right_way)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ChatMember.objects.all().count(), len(self.chatmembers) + 1)

#### Modification requests
    def test_update_wrong_way(self):
        # Has to use the change_role function to change a ChatMember
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.chatmember_url % self.chatmembers[2].id, {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(reload(self.chatmembers[2]), self.chatmembers[2])

    def test_update_unauthed(self):
        # Unauthed client cannot update a chatmember
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(reload(self.chatmembers[2]), self.chatmembers[2])

    def test_update_forbidden(self):
        # Client cannot update a chatmember if he isn't admin of the associated chat
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(reload(self.chatmembers[2]), self.chatmembers[2])

    def test_update_forbidden2(self):
        # Client cannot update a chatmember if it is the creator of the associated chat
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(reload(self.chatmembers[0]), self.chatmembers[0])

    def test_update_forbidden3(self):
        # Client cannot update a chatmember if it is not a member of the right chat
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(reload(self.chatmembers[2]), self.chatmembers[2])

    def test_update_non_existent_chat(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(10), {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(reload(self.chatmembers[2]), self.chatmembers[2])

    def test_update_non_existent_chatmember(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_ok_admin(self):
        # Client can update a chatmember if he has clearance
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "admin", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(reload(self.chatmembers[2]).is_creator)
        self.assertTrue(reload(self.chatmembers[2]).is_admin)
        self.assertTrue(reload(self.chatmembers[2]).is_member)
        self.assertFalse(reload(self.chatmembers[2]).is_banned)

    def test_update_ok_member_from_admin(self):
        # Client can update a chatmember if he has clearance
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "member", "chatmember_id": 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(reload(self.chatmembers[3]).is_creator)
        self.assertFalse(reload(self.chatmembers[3]).is_admin)
        self.assertTrue(reload(self.chatmembers[3]).is_member)
        self.assertFalse(reload(self.chatmembers[3]).is_banned)

    def test_update_ok_ragequit(self):
        # Client can update a chatmember if he has clearance
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "leave", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(reload(self.chatmembers[2]).is_creator)
        self.assertFalse(reload(self.chatmembers[2]).is_admin)
        self.assertFalse(reload(self.chatmembers[2]).is_member)
        self.assertFalse(reload(self.chatmembers[2]).is_banned)

    def test_update_not_self_ragequit(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "leave", "chatmember_id": 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ok_come_back(self):
        # Client can update a chatmember if he has clearance
        self.client.force_authenticate(user=self.users[5])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "member", "chatmember_id": 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(reload(self.chatmembers[5]).is_creator)
        self.assertFalse(reload(self.chatmembers[5]).is_admin)
        self.assertTrue(reload(self.chatmembers[5]).is_member)
        self.assertFalse(reload(self.chatmembers[5]).is_banned)

    def test_update_not_self_come_back(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "member", "chatmember_id": 6})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_ok_unban(self):
        # Client can update a chatmember if he has clearance
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.change_role_chatmember_url.format(self.chats[0].id), {'role': "member", "chatmember_id": 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(reload(self.chatmembers[4]).is_creator)
        self.assertFalse(reload(self.chatmembers[4]).is_admin)
        self.assertTrue(reload(self.chatmembers[4]).is_member)
        self.assertFalse(reload(self.chatmembers[4]).is_banned)
