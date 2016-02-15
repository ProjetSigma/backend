from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.models.cluster import Cluster
from sigma_core.serializers.group import GroupSerializer
from sigma_core.serializers.cluster import BasicClusterSerializer
from sigma_core.tests.factories import UserFactory, GroupFactory, GroupMemberFactory, ClusterFactory, AdminUserFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class ClusterVisibilityTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super().setUpTestData()

        # Test situation
        # Cluster1:
        #   User1.1
        #       -> Group0
        #       -> Group1
        #   User1.2
        #       -> Group0
        #
        # Cluster2:
        #   User2.1:
        #       -> Group1
        # AdminUser

        # Clusters
        self.clusters = ClusterFactory.create_batch(2)

        # Users
        self.c1_users = UserFactory.create_batch(2)
        for user in self.c1_users:
            user.clusters.add(self.clusters[0])
            user.save()
        GroupMemberFactory(user=self.c1_users[0], group=self.clusters[0], perm_rank=1)
        GroupMemberFactory(user=self.c1_users[1], group=self.clusters[0], perm_rank=1)
        self.c2_users  = UserFactory.create_batch(1)
        for user in self.c2_users:
            user.clusters.add(self.clusters[1])
            user.save()
        GroupMemberFactory(user=self.c2_users[0], group=self.clusters[1], perm_rank=1)

        self.admin = AdminUserFactory()

        # Create groups
        self.groups = GroupFactory.create_batch(2)
        # Group0
        GroupMemberFactory(user=self.c1_users[0], group=self.groups[0], perm_rank=1)
        GroupMemberFactory(user=self.c1_users[1], group=self.groups[0], perm_rank=1)
        # Group1
        GroupMemberFactory(user=self.c1_users[0], group=self.groups[1], perm_rank=1)
        GroupMemberFactory(user=self.c2_users[0], group=self.groups[1], perm_rank=1)

        # Routes
        self.user_route = "/user/%d/"

    def test_get_other_cluster_not_visible_user(self):
        # Diff cluster, no common group
        self.client.force_authenticate(user=self.c2_users[0])
        response = self.client.get(self.user_route % self.c1_users[1].id)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_other_cluster_one_mship_visible(self):
        # Diff cluster, common group
        self.client.force_authenticate(user=self.c2_users[0])
        response = self.client.get(self.user_route % self.c1_users[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('memberships')), 1) # One common Group
        self.assertEqual(response.data.get('memberships')[0].get('group').get('id'), self.groups[1].id)

    def test_get_same_cluster(self):
        # Same cluster, one group
        self.client.force_authenticate(user=self.c1_users[0])
        response = self.client.get(self.user_route % self.c1_users[1].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get('memberships')), 2) # Same cluster, see everything
