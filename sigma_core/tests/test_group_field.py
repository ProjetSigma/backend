import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field import GroupField
from sigma_core.models.validator import Validator
from sigma_core.tests.factories import UserFactory, GroupFieldFactory, GroupFactory, GroupMemberFactory


class GroupFieldTests(APITestCase):
    fixtures = ['fixtures_prod.json']
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.group_field_url = "/group-field/"

        # Group open to anyone
        self.group = GroupFactory()

        # Users already in group
        # User[0]: Not in Group
        # User[1]: Requested join, not accepted
        # User[2]: Group member
        # User[3]: Group admin
        self.users = [UserFactory(), UserFactory(), UserFactory(), UserFactory()]
        # Associated GroupMember
        self.group_member = [
                None,
                GroupMemberFactory(user=self.users[1], group=self.group, perm_rank=0),
                GroupMemberFactory(user=self.users[2], group=self.group, perm_rank=1),
                GroupMemberFactory(user=self.users[3], group=self.group, perm_rank=Group.ADMINISTRATOR_RANK)
            ]
        self.group_field = GroupFieldFactory(group=self.group, validator=Validator.objects.all().get(html_name=Validator.VALIDATOR_NONE), validator_values="{}")

        # Misc
        self.new_field_data = {"group": self.group.id,
            "name": "Example Group Field",
            "validator": Validator.VALIDATOR_NONE,
            "validator_values": {}}

    def test_imported_validators(self):
        self.assertTrue(Validator.objects.all().filter(html_name=Validator.VALIDATOR_NONE).exists())

    #################### TEST GROUP FIELD CREATION ########################
    def try_create(self, user):
        self.client.force_authenticate(user=user)
        resp = self.client.post(self.group_field_url, self.new_field_data)
        return resp.status_code

    def test_create_not_authed(self):
        self.assertEqual(self.try_create(None), status.HTTP_401_UNAUTHORIZED)

    def test_create_not_group_member(self):
        self.assertEqual(self.try_create(self.users[0]), status.HTTP_403_FORBIDDEN)

    def test_create_not_group_accepted(self):
        self.assertEqual(self.try_create(self.users[1]), status.HTTP_403_FORBIDDEN)

    def test_create_not_group_admin(self):
        self.assertEqual(self.try_create(self.users[2]), status.HTTP_403_FORBIDDEN)

    def test_create_ok(self):
        self.assertEqual(self.try_create(self.users[3]), status.HTTP_201_CREATED)

    #################### TEST GROUP FIELD DELETION ########################
    def try_delete(self, user):
        self.client.force_authenticate(user=user)
        resp = self.client.delete(self.group_field_url + str(self.group_field.id) + "/")
        return resp.status_code

    def test_delete_not_authed(self):
        self.assertEqual(self.try_delete(None), status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(GroupField.objects.all().filter(id=self.group_field.id).exists())

    def test_delete_not_group_member(self):
        self.assertEqual(self.try_delete(self.users[0]), status.HTTP_404_NOT_FOUND)
        self.assertTrue(GroupField.objects.all().filter(id=self.group_field.id).exists())

    def test_delete_not_group_accepted(self):
        self.assertEqual(self.try_delete(self.users[1]), status.HTTP_403_FORBIDDEN)
        self.assertTrue(GroupField.objects.all().filter(id=self.group_field.id).exists())

    def test_delete_not_group_admin(self):
        self.assertEqual(self.try_delete(self.users[2]), status.HTTP_403_FORBIDDEN)
        self.assertTrue(GroupField.objects.all().filter(id=self.group_field.id).exists())

    def test_delete_ok(self):
        self.assertEqual(self.try_delete(self.users[3]), status.HTTP_204_NO_CONTENT)
        self.assertFalse(GroupField.objects.all().filter(id=self.group_field.id).exists())

    #################### TEST GROUP FIELD LIST    ########################
    def test_list_not_authed(self):
        resp = self.client.get(self.group_field_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_no_group(self):
        self.client.force_authenticate(user=self.users[0])
        resp = self.client.get(self.group_field_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(any(resp.data))

    def test_list_in_group(self):
        from sigma_core.serializers.group_field import GroupFieldSerializer
        self.client.force_authenticate(user=self.users[2])
        resp = self.client.get(self.group_field_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0], GroupFieldSerializer(self.group_field).data)
