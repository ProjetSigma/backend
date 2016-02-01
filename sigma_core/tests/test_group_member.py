import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer
from sigma_core.tests.factories import UserFactory, AdminUserFactory, GroupFactory, GroupMemberFactory


class OpenGroupMemberCreationTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.members_url = "/group-member/"
        self.member_url = self.members_url + "%d/"

        # Group open to anyone
        self.group = GroupFactory()
        self.group.default_member_rank = 1
        self.group.save()

        # Users already in group
        self.users = [UserFactory()]
        # Associated GroupMember
        self.group_member1 = GroupMember(user=self.users[0], group=self.group, perm_rank=Group.ADMINISTRATOR_RANK)

        # Testing user
        self.user = UserFactory()

        # Misc
        self.new_membership_data = {"group": self.group.id, "user": self.user.id}

    def test_create_not_authed(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_not_for_self(self):
        # Attempt to add somebody else to a group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_success(self):
        # Succesful attempt to join an open group
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['perm_rank'], self.group.default_member_rank)


class RequestGroupMemberCreationTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.members_url = "/group-member/"
        self.accept_join_requests_url = self.members_url + "%d/accept_join_request/"

        # Group with membership request
        self.group = GroupFactory(default_member_rank=0, req_rank_accept_join_requests=5)

        # Users already in group
        self.users = UserFactory.create_batch(3)
        # Associated GroupMember
        self.group_member1 = GroupMemberFactory(user=self.users[0], group=self.group, perm_rank=Group.ADMINISTRATOR_RANK) # can validate requests
        self.group_member2 = GroupMemberFactory(user=self.users[1], group=self.group, perm_rank=1) # cannot validate requests
        self.group_member3 = GroupMemberFactory(user=self.users[2], group=self.group, perm_rank=0) # request to be validated

        # Testing user
        self.user = UserFactory()

        # Misc
        self.new_membership_data = {"group": self.group.id, "user": self.user.id}

    def test_create_not_authed(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_success(self):
        # Succesful attempt to request group membership
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['perm_rank'], self.group.default_member_rank)

    def test_validate_forbidden(self):
        # Attempt to validate a request but not enough permission
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.accept_join_requests_url % self.group_member3.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_validate_success(self):
        # Succesful attempt to validate a request
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.accept_join_requests_url % self.group_member3.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['perm_rank'], 1)


class InvitationGroupMemberCreationTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.members_url = "/group-member/"

        # Group with invitation only
        self.group = GroupFactory(req_rank_invite=5, default_member_rank=-1, visibility=Group.VIS_PRIVATE)

        # Testing user
        self.users = UserFactory.create_batch(2)
        self.memberships = [
            None,
            GroupMemberFactory(user=self.users[1], group=self.group, perm_rank=self.group.req_rank_invite)
        ]

        # Misc
        self.new_membership_data = {"group": self.group.id, "user": self.users[0].id}

    def test_create_not_authed(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_forbidden(self):
        # Can't join this Group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_already_group_member(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_self_forbidden(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.members_url, self.new_membership_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class InvitationGroupMemberInvitationWorkflowTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()

        # Routes
        self.members_url = "/group-member/"
        self.group_invite_url = "/group/%d/invite/";
        self.group_invite_accept_url = "/group/%d/invite_accept/";

        # Group with invitation only
        self.group = GroupFactory(req_rank_invite=5, default_member_rank=-1)

        # Testing user
        self.users = UserFactory.create_batch(2)
        self.memberships = [
            None,
            GroupMemberFactory(user=self.users[1], group=self.group, perm_rank=self.group.req_rank_invite)
        ]

    def test_invite_not_authed(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(self.group_invite_url % (self.group.id), {"user": self.users[0].id} )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invite_forbidden(self):
        # Attempt to get group membership
        self.client.force_authenticate(user=self.users[0])
        response = self.client.put(self.group_invite_url % (self.group.id), {"user": self.users[0].id} )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_already_group_member(self):
        # Attempt to get group membership
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.group_invite_url % (self.group.id), {"user": self.users[1].id} )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_ok(self):
        # User0 invites User1 to group
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.group_invite_url % (self.group.id), {"user": self.users[0].id} )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invite_accept(self):
        self.test_invite_ok()
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.members_url, {"user": self.users[0].id, "group": self.group.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
