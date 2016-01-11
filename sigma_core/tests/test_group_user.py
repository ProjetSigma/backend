import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory, GroupFactory, GroupMemberFactory
from sigma_core.tests.test_group_routes import GroupSubRoutesGroupMembershipTests
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer
from sigma_core.models.user import User
from sigma_core.models.group import Group

class GroupUserTests(GroupSubRoutesGroupMembershipTests, APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        GroupSubRoutesGroupMembershipTests.setUpTestData('user')
