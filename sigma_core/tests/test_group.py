import json

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, GroupFactory
from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer


class GroupTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(GroupTests, self).setUpTestData()

        self.group = GroupFactory()
        self.user = UserFactory()

        serializer = GroupSerializer(self.group)
        self.group_data = serializer.data
        self.group_url = '/group/%d/' % self.group.id

        self.groups_list = [self.group]

        self.new_group_data = {'name': 'New group'}

    #### List requests
    def test_get_groups_list_unauthed(self):
        # Client not authenticated
        response = self.client.get('/group/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_groups_list_forbidden(self):
    #     # Client authenticated but has no permission
    #     self.client.force_authenticate(group=self.user)
    #     response = self.client.get('/group/')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_groups_list_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/group/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.groups_list))

    #### Get requests
    def test_get_group_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.group_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_group_forbidden(self):
    #     response = self.client.get(self.group_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_group_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.group_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.group_data)

    #### Create requests

    #### Modification requests

    #### Deletion requests
