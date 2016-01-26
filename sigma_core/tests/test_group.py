import json

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer
from sigma_core.tests.factories import UserFactory, GroupFactory, GroupMemberFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class GroupTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(GroupTests, self).setUpTestData()

        # Groups
        self.groups = GroupFactory.create_batch(2)
        self.groups[0].visibility = Group.VIS_PUBLIC
        self.groups[0].save()
        self.groups[1].visibility = Group.VIS_PRIVATE
        self.groups[1].req_rank_invite = 5
        self.groups[1].save()

        # Users
        self.users = UserFactory.create_batch(3)

        # Memberships
        self.member1 = GroupMemberFactory(user=self.users[1], group=self.groups[1], perm_rank=1)
        self.member2 = GroupMemberFactory(user=self.users[2], group=self.groups[1], perm_rank=Group.ADMINISTRATOR_RANK)

        serializer = GroupSerializer(self.groups[0])
        self.group_data = serializer.data
        self.groups_url = "/group/"
        self.group_url = self.groups_url + "%d/"

        self.new_group_data = {"name": "New group"}
        self.invite_data = {"user": self.users[0].id}

    #### List requests
    def test_get_groups_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_groups_list_forbidden(self):
    #     # Client authenticated but has no permission
    #     self.client.force_authenticate(group=self.users[0])
    #     response = self.client.get(self.group_url % self.groups[1].id)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_groups_list_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.groups))

    #### Get requests
    def test_get_group_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.group_url % self.groups[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_group_forbidden(self):
        # Non-member wants to see a private group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[1].id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_group_ok(self):
        # Client wants to see a public group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.group_data)

    #### Invitation requests
    def test_invite_unauthed(self):
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_invite_forbidden(self):
    #     # Client has not perms to invite
    #     self.client.force_authenticate(user=self.users[1])
    #     response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_ok(self):
        # Client has perms to invite
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.groups[1], reload(self.users[0]).invited_to_groups.all())

    #### Create requests

    #### Modification requests

    #### Deletion requests
