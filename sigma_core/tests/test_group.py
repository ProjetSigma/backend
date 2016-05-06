import json

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer
from sigma_core.tests.factories import UserFactory, GroupFactory, GroupMemberFactory, ClusterFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class GroupTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(GroupTests, self).setUpTestData()

        # Schools
        self.schools = ClusterFactory.create_batch(1)

        # Groups
        self.groups = [GroupFactory(is_private=False), GroupFactory(is_private=True, req_rank_invite=5)]

        # Users
        self.users = UserFactory.create_batch(3)

        # Memberships
        self.member1 = GroupMemberFactory(user=self.users[1], group=self.groups[1], perm_rank=1)
        self.member2 = GroupMemberFactory(user=self.users[2], group=self.groups[1], perm_rank=Group.ADMINISTRATOR_RANK)
        self.student1 = GroupMemberFactory(user=self.users[0], group=self.schools[0], perm_rank=1)
        self.student2 = GroupMemberFactory(user=self.users[1], group=self.schools[0], perm_rank=Group.ADMINISTRATOR_RANK) # School admin
        self.student3 = GroupMemberFactory(user=self.users[2], group=self.schools[0], perm_rank=1)

        serializer = GroupSerializer(self.groups[0])
        self.group_data = serializer.data
        self.update_group_data = self.group_data.copy()
        self.update_group_data['name'] = "Another name"
        self.groups_url = "/group/"
        self.group_url = self.groups_url + "%d/"

        self.new_private_group_data = {"name": "New group", "is_private": True}
        self.new_public_group_data = {"name": "New group", "is_private": False, "resp_group": self.schools[0].id}
        self.invite_data = {"user": self.users[0].id}

    #### List requests
    def test_get_groups_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_groups_list_limited(self):
        # Client authenticated and can see public groups
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.groups[0].id, [d['id'] for d in response.data]) # User can only see groups[0]
        self.assertNotIn(self.groups[1].id, [d['id'] for d in response.data])

    def test_get_groups_list_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.groups_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.groups[0].id, [d['id'] for d in response.data]) # groups[0] is public and user is member of groups[1]
        self.assertIn(self.groups[1].id, [d['id'] for d in response.data])

    #### Get requests
    def test_get_group_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.group_url % self.groups[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_group_forbidden(self):
        # Non-member wants to see a is_private group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.group_url % self.groups[1].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_invite_forbidden(self):
        # Client has not perms to invite
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invite_ok(self):
        # Client has perms to invite
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.groups[1], reload(self.users[0]).invited_to_groups.all())

    def test_invite_duplicate(self):
        self.test_invite_ok()
        response = self.client.put((self.group_url + "invite/") % self.groups[1].id, self.invite_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #### Create requests
    def test_create_unauthed(self):
        # Client is not authenticated
        response = self.client.post(self.groups_url, self.new_private_group_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_private_group(self):
        # Everybody can create a is_private group
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.groups_url, self.new_private_group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.new_private_group_data['name'])
        self.assertEqual(response.data['is_private'], True)
        Group.objects.get(pk=response.data['id']).delete()

    def test_create_public_group_ok(self):
        # Only school andmins and Sigma admins can create association groups
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.groups_url, self.new_public_group_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_private'], False)

    #### Modification requests
    def test_update_unauthed(self):
        response = self.client.put(self.group_url % self.groups[1].id, self.update_group_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_forbidden(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.put(self.group_url % self.groups[1].id, self.update_group_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ok(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.put(self.group_url % self.groups[1].id, self.update_group_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reload(self.groups[1]).name, self.update_group_data['name'])

    #### Deletion requests
