import json

from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.models.group_field import GroupField
from sigma_core.models.validator import Validator
from sigma_core.tests.factories import AdminUserFactory, UserFactory, GroupFieldFactory, GroupFactory, GroupMemberFactory, GroupMemberValueFactory
from sigma_core.serializers.group_member_value import GroupMemberValueSerializer


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
        self.users = UserFactory.create_batch(5) + [AdminUserFactory()]

        # Associated GroupMember
        self.group_member = [
            None,
            GroupMemberFactory(user=self.users[1], group=self.group, perm_rank=0),
            GroupMemberFactory(user=self.users[2], group=self.group, perm_rank=1),
            GroupMemberFactory(user=self.users[3], group=self.group, perm_rank=Group.ADMINISTRATOR_RANK),
            GroupMemberFactory(user=self.users[4], group=self.group, perm_rank=0)
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
                validator_values={"regex": "[^@]+@[^@]+\.[^@]+", "message": "Invalid email"}),
            GroupFieldFactory(group=self.group, validator=self.validator_none, validator_values={}),
        ]

        # And we need a second group
        self.group2 = GroupFactory()
        self.group2_user2 = GroupMemberFactory(user=self.users[4], group=self.group2, perm_rank=1)
        self.group2_fields = [
            # First field does not require any validation
            GroupFieldFactory(group=self.group2, validator=self.validator_none, validator_values={}),
            # Second field must be in the email format
            GroupFieldFactory(group=self.group2,
                validator=self.validator_text,
                validator_values={"regex": "[^@]+@[^@]+\.[^@]+", "message": "Invalid email"}),
            GroupFieldFactory(group=self.group2, validator=self.validator_none, validator_values={}),
        ]

        # Create some values
        GroupMemberValueFactory(field=self.group2_fields[0], membership=self.group2_user2, value="TextFieldValue1")
        GroupMemberValueFactory(field=self.group2_fields[1], membership=self.group2_user2, value="my@email.com")
        GroupMemberValueFactory(field=self.group_fields[2], membership=self.group_member[2], value="Field3Value__user2")
        GroupMemberValueFactory(field=self.group_fields[2], membership=self.group_member[3], value="Field3Value__user3")


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

    def test_create_group_field_validation_fail(self):
        self.try_create(2, self.group_member[2].id, self.group_fields[1].id, "ABC", status.HTTP_400_BAD_REQUEST)

    # Create OK cases
    def test_create_group_member_not_accepted(self):
        self.try_create(1, self.group_member[1].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_group_member(self):
        self.try_create(2, self.group_member[2].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_group_admin(self):
        self.try_create(3, self.group_member[3].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_sigma_admin(self):
        self.try_create(5, self.group_member[3].id, self.group_fields[0].id, "ABC", status.HTTP_201_CREATED)

    def test_create_group_field_validation_ok(self):
        self.try_create(2, self.group_member[2].id, self.group_fields[1].id, "some@email.com", status.HTTP_201_CREATED)

    def test_create_group_field_duplicate(self):
        self.try_create(2, self.group_member[2].id, self.group_fields[1].id, "some@email.com", status.HTTP_201_CREATED)
        self.try_create(2, self.group_member[2].id, self.group_fields[1].id, "some@email2.com", status.HTTP_400_BAD_REQUEST)

    #################### TEST GROUP MEMBER VALUE LISTING #######################
    def try_list(self, userIdx, expectedHttpResponse):
        if userIdx >= 0:
            self.client.force_authenticate(user=self.users[userIdx])
        resp = self.client.get(self.group_field_url)
        self.assertEqual(resp.status_code, expectedHttpResponse)
        return resp.data

    # Basic permission checks
    def test_list_not_authed(self):
        self.try_list(-1, status.HTTP_401_UNAUTHORIZED)

    def test_list_not_group_member(self):
        r = self.try_list(0, status.HTTP_200_OK)
        self.assertEqual(len(r), 0)

    def test_list_not_accepted(self):
        r = self.try_list(1, status.HTTP_200_OK)
        self.assertEqual(len(r), GroupMemberValue.objects.all().filter(membership=self.group_member[1]).count())

    def test_list_group_member(self):
        r = self.try_list(2, status.HTTP_200_OK)
        #import pdb; pdb.set_trace()
        self.assertEqual(len(r), GroupMemberValue.objects.all().filter(membership__group=self.group.id).count())

    def test_list_group_member2(self):
        # User4 is in a different group.
        r = self.try_list(4, status.HTTP_200_OK)
        self.assertEqual(len(r), GroupMemberValue.objects.all().filter(membership__group=self.group2.id).count())
        self.assertEqual(len(r), 2)

    def test_list_sigma_admin(self):
        r = self.try_list(5, status.HTTP_200_OK)
        self.assertEqual(len(r), GroupMemberValue.objects.all().count())

    #################### TEST GROUP MEMBER VALUE LISTING #######################
    def try_update(self, userIdx, memberValue, fieldNewValue, expectedHttpResponse):
        if userIdx >= 0:
            self.client.force_authenticate(user=self.users[userIdx])
        memberValue.value = fieldNewValue
        field_value = GroupMemberValueSerializer(memberValue).data
        resp = self.client.put("%s%d/" % (self.group_field_url, memberValue.id), field_value)
        self.assertEqual(resp.status_code, expectedHttpResponse)

    def test_update_not_authed(self):
        self.try_update(-1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), "ABC", status.HTTP_401_UNAUTHORIZED)

    def test_update_not_group_member(self):
        self.try_update(0, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), "ABC", status.HTTP_404_NOT_FOUND)

    def test_update_self_invalid(self):
        self.try_update(1, GroupMemberValueFactory(field=self.group_fields[1], value="email@domain.com", membership=self.group_member[1]), "Not_A_Valid_Email", status.HTTP_400_BAD_REQUEST)

    def test_update_membership(self):
        self.client.force_authenticate(user=self.users[1])
        memberValue = GroupMemberValueFactory(field=self.group_fields[1], value="email@domain.com", membership=self.group_member[1])
        memberShip2 = GroupMemberFactory(user=self.users[1], group=self.group2, perm_rank=1)
        memberValue.membership = memberShip2
        field_value = GroupMemberValueSerializer(memberValue).data
        resp = self.client.put("%s%d/" % (self.group_field_url, memberValue.id), field_value)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_self_ok(self):
        self.try_update(1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), "ABC", status.HTTP_200_OK)

    def test_update_sigma_admin(self):
        self.try_update(5, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), "ABC", status.HTTP_200_OK)

    #################### TEST GROUP MEMBER VALUE RETRIEVE ######################
    def try_retrieve(self, userIdx, memberValue, expectedHttpResponse):
        if userIdx >= 0:
            self.client.force_authenticate(user=self.users[userIdx])
        resp = self.client.get("%s%d/" % (self.group_field_url, memberValue.id))
        self.assertEqual(resp.status_code, expectedHttpResponse)

    def test_retrieve_not_authed(self):
        self.try_retrieve(-1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_not_group_member(self):
        self.try_retrieve(0, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_404_NOT_FOUND)

    def test_retrieve_other_member_but_not_accepted(self):
        self.try_retrieve(1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_404_NOT_FOUND)

    def test_retrieve_self_value_not_accepted(self):
        self.try_retrieve(1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_200_OK)

    def test_retrieve_other_member_ok(self):
        self.try_retrieve(2, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_200_OK)

    def test_retrieve_sigma_admin(self):
        self.try_retrieve(5, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_200_OK)

    #################### TEST GROUP MEMBER VALUE DESTROY #######################
    def try_delete(self, userIdx, memberValue, expectedHttpResponse):
        if userIdx >= 0:
            self.client.force_authenticate(user=self.users[userIdx])
        resp = self.client.delete("%s%d/" % (self.group_field_url, memberValue.id))
        self.assertEqual(resp.status_code, expectedHttpResponse)

    def test_delete_not_authed(self):
        self.try_delete(-1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_group_member(self):
        self.try_delete(0, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_404_NOT_FOUND)

    def test_delete_other_member_but_not_accepted(self):
        self.try_delete(1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_404_NOT_FOUND)

    def test_delete_other_member(self):
        self.try_delete(3, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[2]), status.HTTP_403_FORBIDDEN)

    def test_delete_self_value_not_accepted(self):
        self.try_delete(1, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_204_NO_CONTENT)

    def test_delete_sigma_admin(self):
        self.try_delete(5, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_204_NO_CONTENT)

    def test_delete_other_member(self):
        self.try_delete(2, GroupMemberValueFactory(field=self.group_fields[0], value="Blah", membership=self.group_member[1]), status.HTTP_403_FORBIDDEN)
