import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.models.group_field import GroupField
from sigma_core.models.validator import Validator
from sigma_core.tests.factories import UserFactory, GroupFieldFactory, GroupFactory, GroupMemberFactory


class GroupFieldTests(APITestCase):
    fixtures = ['fixtures_prod.json'] # Import Validators
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.group_field_url = "/group-member-value/"

        # Create the base Group
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
        # Let's add some custom fields to this Group
        self.validator_none = Validator.objects.all().get(html_name=Validator.VALIDATOR_NONE)
        self.validator_text = Validator.objects.all().get(html_name=Validator.VALIDATOR_TEXT)
        self.group_fields = [
            # First field does not require any validation
            GroupFieldFactory(group=self.group, validator=self.validator_none, validator_values={}),
            # Second field must be in the email format
            GroupFieldFactory(group=self.group,
                validator=self.validator_text,
                validator_values={"regex": "[^@]+@[^@]+\.[^@]+", "message": "Invalid email"})
        ]

        # And we need a second group
        self.group2 = GroupFactory()
        self.group2_user2 = GroupMemberFactory(user=self.users[2], group=self.group2, perm_rank=1)


    #################### TEST GROUP MEMBER VALUE CREATION ######################
    def try_create(self, userIdx, membershipIdx, fieldIdx, fieldValue, expectedHttpResponse):
        if userIdx >= 0:
            self.client.force_authenticate(user=self.users[userIdx])
        field_value = {
            "membership": membershipIdx,
            "field": fieldIdx,
            "value": fieldValue
        }
        resp = self.client.post(self.group_field_url, field_value)
        self.assertEqual(resp.status_code, expectedHttpResponse)

    # Basic permission checks
    def test_create_not_authed(self):
        self.try_create(-1, -1, self.group_fields[0].id, "ABC", status.HTTP_401_UNAUTHORIZED)

    def test_create_not_group_member(self):
        self.try_create(0, 0, self.group_fields[0].id, "ABC", status.HTTP_400_BAD_REQUEST)

    # Some possible hack attempts now
    def test_create_not_group_member2(self):
        self.try_create(0, self.group_member[2].id, self.group_fields[0].id, "ABC", status.HTTP_400_BAD_REQUEST)

    def test_create_other_user(self):
        self.try_create(1, self.group_member[2].id, self.group_fields[0].id, "ABC", status.HTTP_400_BAD_REQUEST)

    def test_create_group_field_mismatch(self):
        self.try_create(2, self.group2_user2.id, self.group_fields[0].id, "ABC", status.HTTP_400_BAD_REQUEST)

    # Create OK cases
    def test_create_group_member_not_accepted(self):
        self.try_create(1, self.group_member[1].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_group_member(self):
        self.try_create(2, self.group_member[2].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_group_admin(self):
        self.try_create(3, self.group_member[3].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)
