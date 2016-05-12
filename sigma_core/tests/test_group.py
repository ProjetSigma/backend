import json

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer
from sigma_core.tests.factories import UserFactory, AdminUserFactory, GroupFactory, GroupMemberFactory, ClusterFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class GroupTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        # Summary: 1 cluster, 4 users + 1 admin, 5 groups (+1 group for the cluster)
        # Users #1 and #2 are in cluster #1
        # User #5 is Sigma admin
        # Group #1 is public, others are private
        # Users #1 and #2 are members of group #3; user #1 is group admin
        # Users #3 and #4 are members of group #2; user #3 has invitation clearance, not user #4
        # User #4 is member of group #5
        # User #1 is invited to group #5
        # Group #4 is acknowledged by cluster #1

        super(GroupTests, self).setUpTestData()
        self.clusters = ClusterFactory.create_batch(1)
        self.groups = GroupFactory.create_batch(5, is_private=True)
        self.users = UserFactory.create_batch(3) + [AdminUserFactory()]

        # Group #1 is public
        self.groups[0].is_private = False
        self.groups[0].default_member_rank = 1
        self.groups[0].name = "Public group without invitation"
        self.groups[0].save()

        # Group #2 clearance parameters
        self.groups[1].req_rank_invite = 5
        self.groups[1].save()

        # Users in cluster
        self.users[0].clusters.add(self.clusters[0])
        self.users[1].clusters.add(self.clusters[0])
        GroupMemberFactory(user=self.users[0], group=self.clusters[0].group_ptr)
        GroupMemberFactory(user=self.users[1], group=self.clusters[0].group_ptr)
        # Users in group #2
        GroupMemberFactory(user=self.users[2], group=self.groups[1], perm_rank=self.groups[1].req_rank_invite)
        GroupMemberFactory(user=self.users[3], group=self.groups[1])
        # Users in group #3
        GroupMemberFactory(user=self.users[0], group=self.groups[2], perm_rank=Group.ADMINISTRATOR_RANK)
        GroupMemberFactory(user=self.users[1], group=self.groups[2])
        # Users in group #5
        GroupMemberFactory(user=self.users[3], group=self.groups[4])
        # User #1 is invited to group #5
        self.users[0].invited_to_groups.add(self.groups[4])

        # TODO: GroupAcknowledgment

        self.groups_url = "/group/"
        self.group_url = self.groups_url + "%d/"

        self.new_private_group_data = {"name": "New private group", "is_private": True}
        self.new_public_group_data = {"name": "New public group", "is_private": False}
        self.invite_data = {"user": self.users[0].id}

#### Model methods test
    def test_model_group(self):
        self.assertEqual(self.clusters[0].group_ptr.members_count, 2)
        self.assertFalse(self.groups[1].can_anyone_join())
        self.assertTrue(self.groups[0].can_anyone_join())
        self.assertEqual(self.groups[0].__str__(), "Public group without invitation")

#### List requests
    def test_get_groups_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_groups_list_limited_1(self):
        # Client authenticated and can see limited list of groups
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertIn(self.groups[0].id, [d['id'] for d in response.data])
        self.assertNotIn(self.groups[1].id, [d['id'] for d in response.data])

    def test_get_groups_list_limited_2(self):
        # Client authenticated and can see limited list of groups
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)
        self.assertNotIn(self.groups[4].id, [d['id'] for d in response.data])

    def test_get_groups_list_admin(self):
        # Client authenticated and can see limited list of groups
        self.client.force_authenticate(user=self.users[-1])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 6)

#### Get requests
    def test_get_group_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.group_url % self.groups[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_group_public(self):
        # Client can see public group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_private(self):
        # Client cannot see private group if he's not a member
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[1].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_group_member(self):
        # Client can see private group if he is a member
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[2].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_acknowledged(self):
        # Client can see private group if it has been acknowledged by one of his groups
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[3].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_group_invited(self):
        # Client can see private if he has been invited to it
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[4].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#### Create requests
    def test_create_unauthed(self):
        # Client is not authenticated
        response = self.client.post(self.groups_url, self.new_private_group_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_private_group(self):
        # Everybody can create a group
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.groups_url, self.new_private_group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.new_private_group_data['name'])
        self.assertEqual(response.data['is_private'], True)
        Group.objects.get(pk=response.data['id']).delete()

    def test_create_public_group(self):
        # Everybody can create a public group
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.groups_url, self.new_public_group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_private'], False)
        Group.objects.get(pk=response.data['id']).delete()

#### Modification requests
    def test_update_unauthed(self):
        # Unauthed client cannot update a group
        update_group_data = GroupSerializer(self.groups[2]).data
        response = self.client.put(self.group_url % self.groups[2].id, update_group_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_forbidden(self):
        # Client cannot update a group if he hasn't clearance
        update_group_data = GroupSerializer(self.groups[2]).data
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.group_url % self.groups[2].id, update_group_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ok(self):
        # Client can update a group if he has clearance
        update_group_data = GroupSerializer(self.groups[2]).data
        self.client.force_authenticate(user=self.users[0])
        old_name = update_group_data['name']
        update_group_data['name'] = "A new name"
        response = self.client.put(self.group_url % self.groups[2].id, update_group_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reload(self.groups[2]).name, update_group_data['name'])
        # Guarantee independance of tests
        self.groups[2].name = old_name
        self.groups[2].save()

    def test_update_group_by_acknowledgment_delegation(self):
        pass

#### Deletion requests

#### Invitation requests
    def test_invite_unauthed(self):
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invite_forbidden(self):
        # Client has not perms to invite
        self.client.force_authenticate(user=self.users[3])
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_ok(self):
        # Client has perms to invite
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.groups[1], reload(self.users[0]).invited_to_groups.all())
        # Guarantee independance of tests
        self.users[0].invited_to_groups.remove(self.groups[1])

    def test_invite_duplicate(self):
        # Client wants to invite someone who has already received an invitation
        self.client.force_authenticate(user=self.users[3])
        response = self.client.put((self.group_url + "invite/") % self.groups[4].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invite_already_member(self):
        # Client wants to invite a member
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put((self.group_url + "invite/") % self.groups[2].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
