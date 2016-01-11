import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory, GroupFactory, GroupMemberFactory
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer
from sigma_core.models.user import User
from sigma_core.models.group import Group

class GroupSubRoutesGroupMembershipTests():
    @classmethod
    def setUpTestData(self, route_name):
        self.route_name_list = '/group/%d/' + route_name + '/'
        self.route_name_retrieve = '/group/%d/' + route_name + '/%d/'
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.user4 = UserFactory()
        self.admin_user = AdminUserFactory()

        # Create a group for 1, 2 and 3
        # 1 is admin
        # 2 is member
        # 3 requests a join
        self.group12 = GroupFactory()
        self.user1group12 = GroupMemberFactory(user=self.user1, group=self.group12, perm_rank=Group.ADMINISTRATOR_RANK)
        self.user2group12 = GroupMemberFactory(user=self.user2, group=self.group12, perm_rank=1)
        self.user3group12 = GroupMemberFactory(user=self.user3, group=self.group12, perm_rank=0)


#### List requests
    def test_list_user_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.route_name_list % (self.group12.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_user_forbidden_client_not_in_group(self):
        # Client authenticated but is not in Group
        self.client.force_authenticate(user=self.user4)
        response = self.client.get(self.route_name_list % (self.group12.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_user_forbidden_join_request_not_confirmed(self):
        # Client authenticated, in Group, but not accepted in Group
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.route_name_list % (self.group12.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.route_name_list % (self.group12.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#### Get requests
    def test_get_user_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.route_name_retrieve % (self.group12.id, self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_forbidden_client_not_in_group(self):
        # Client authenticated but is not in Group
        self.client.force_authenticate(user=self.user4)
        response = self.client.get(self.route_name_retrieve % (self.group12.id, self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_forbidden_join_request_not_confirmed(self):
        # Client authenticated, in Group, but not accepted in Group
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.route_name_retrieve % (self.group12.id, self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_forbidden_user_not_in_group(self):
        # Client authenticated and in group, but requesting a user not in group
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.route_name_retrieve % (self.group12.id, self.user4.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.route_name_retrieve % (self.group12.id, self.user1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
