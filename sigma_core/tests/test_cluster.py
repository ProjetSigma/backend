from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.models.cluster import Cluster
from sigma_core.serializers.group import GroupSerializer
from sigma_core.serializers.cluster import BasicClusterSerializer
from sigma_core.tests.factories import UserFactory, GroupFactory, GroupMemberFactory, ClusterFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class ClusterTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        # Summary: 2 clusters, 4 users
        # Users #1 and #2 are in cluster #1
        # User #1 is admin of cluster #1
        # User #3 is Sigma admin

        super().setUpTestData()

        # Clusters
        self.clusters = ClusterFactory.create_batch(2)

        # Users
        self.users = UserFactory.create_batch(4)
        self.users[2].is_staff = True # Sigma admin
        self.users[2].save()

        # Memberships
        self.member1 = GroupMemberFactory(user=self.users[0], group=self.clusters[0], perm_rank=Group.ADMINISTRATOR_RANK)
        self.member2 = GroupMemberFactory(user=self.users[1], group=self.clusters[0], perm_rank=1)

        serializer = BasicClusterSerializer(self.clusters[0])
        self.cluster_data = serializer.data
        self.clusters_url = "/cluster/"
        self.cluster_url = self.clusters_url + "%d/"

        self.new_cluster_data = {"name": "Ecole polytechnique", "design": "default"}

#### List requests
    def test_get_clusters_list_unauthed(self):
        # Client not authenticated but can see clusters list
        response = self.client.get(self.clusters_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.clusters))

    def test_get_clusters_list_ok(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.clusters_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.clusters))

#### Get requests
    def test_get_cluster_unauthed(self):
        # Client is not authenticated, can see cluster data but cannot see cluster details (especially members)
        response = self.client.get(self.cluster_url % self.clusters[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('users_ids', response.data)

    def test_get_cluster_forbidden(self):
        # Client wants to see a cluster whose he is not member of
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.cluster_url % self.clusters[1].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('users_ids', response.data)

    def test_get_cluster_ok(self):
        # Client wants to see a cluster to which he belongs
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.cluster_url % self.clusters[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('name', None), self.cluster_data['name'])

#### Create requests
    def test_create_cluster_unauthed(self):
        response = self.client.post(self.clusters_url, self.new_cluster_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_cluster_forbidden(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.clusters_url, self.new_cluster_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_cluster_wrong_data(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.clusters_url, {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cluster_ok(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.clusters_url, self.new_cluster_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cluster = Cluster.objects.filter(pk=response.data['id']).get()
        self.assertEqual(cluster.name, "Ecole polytechnique")
        self.assertEqual(cluster.is_private, False)
        self.assertEqual(cluster.default_member_rank, -1)
        self.assertEqual(cluster.req_rank_invite, Group.ADMINISTRATOR_RANK)

#### Modification requests
    def test_update_cluster_unauthed(self):
        self.cluster_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_cluster_forbidden_1(self):
        self.client.force_authenticate(user=self.users[3])
        self.cluster_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_cluster_forbidden_2(self):
        self.client.force_authenticate(user=self.users[1])
        self.cluster_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_cluster_wrong_data(self):
        self.client.force_authenticate(user=self.users[2])
        self.cluster_data['name'] = ""
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cluster_ok_staff(self):
        self.client.force_authenticate(user=self.users[2])
        self.cluster_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Ecole polytechnique")

    def test_update_cluster_ok_cluster_admin(self):
        self.client.force_authenticate(user=self.users[0])
        self.cluster_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.cluster_url % self.cluster_data['id'], self.cluster_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Ecole polytechnique")

#### Invitation process


#### Deletion requests
