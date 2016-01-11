import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory, GroupFactory, GroupMemberFactory
from sigma_core.tests.test_group_routes import GroupSubRoutesGroupMembershipTests
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer
from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember

class GroupMemberTests(GroupSubRoutesGroupMembershipTests, APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        GroupSubRoutesGroupMembershipTests.setUpTestData('member')
        # Create a group for 1, 2 and 3
        # 1 is admin
        # 2 is member
        # 3 requests a join
        self.group_create_route = '/group/%d/member/' % self.group12.id
        self.new_membership_data = {'group':    self.group12.id,
                                    'user':     self.user4.id}

    def test_create_groupmember_forbidden_not_authed(self):
        response = self.client.post(self.group_create_route, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_groupmember_forbidden_not_group_member(self):
        self.client.force_authenticate(user=self.user4)
        response = self.client.post(self.group_create_route, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_groupmember_forbidden_not_accepted_in_group(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(self.group_create_route, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
