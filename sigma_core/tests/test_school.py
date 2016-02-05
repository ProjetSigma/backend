from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.models.group import Group
from sigma_core.models.school import School
from sigma_core.serializers.group import GroupSerializer
from sigma_core.serializers.school import SchoolSerializer
from sigma_core.tests.factories import UserFactory, GroupFactory, SchoolFactory, GroupMemberFactory


def reload(obj):
    return obj.__class__.objects.get(pk=obj.pk)


class SchoolTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(SchoolTests, self).setUpTestData()

        # Schools
        self.schools = SchoolFactory.create_batch(2)

        # Users
        self.users = UserFactory.create_batch(4)
        self.users[2].is_staff = True # Sigma admin
        self.users[2].save()

        # Memberships
        self.member1 = GroupMemberFactory(user=self.users[0], group=self.schools[0], perm_rank=Group.ADMINISTRATOR_RANK)
        self.member2 = GroupMemberFactory(user=self.users[1], group=self.schools[0], perm_rank=1)

        serializer = SchoolSerializer(self.schools[0])
        self.school_data = serializer.data
        self.schools_url = "/school/"
        self.school_url = self.schools_url + "%d/"

        self.new_school_data = {"name": "Ecole polytechnique", "design": "default"}
        # self.invite_data = {"user": self.users[0].id}

    #### List requests
    def test_get_schools_list_unauthed(self):
        # Client not authenticated but can see schools list
        response = self.client.get(self.schools_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.schools))

    def test_get_schools_list_ok(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.schools_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.schools))

    #### Get requests
    def test_get_school_unauthed(self):
        # Client is not authenticated and cannot see school details (especially members)
        response = self.client.get(self.school_url % self.schools[0].id)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_school_forbidden(self):
        # Client wants to see a a school whose he is not member of
        self.client.force_authenticate(user=self.users[0])
        response = self.client.get(self.school_url % self.schools[1].id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_school_ok(self):
        # Client wants to see a school to which he belongs
        self.client.force_authenticate(user=self.users[1])
        response = self.client.get(self.school_url % self.schools[0].id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.school_data)

    #### Create requests
    def test_create_school_unauthed(self):
        response = self.client.post(self.schools_url, self.new_school_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_school_forbidden(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.schools_url, self.new_school_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_school_wrong_data(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.schools_url, {"name": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_school_ok(self):
        self.client.force_authenticate(user=self.users[2])
        response = self.client.post(self.schools_url, self.new_school_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Ecole polytechnique")
        self.assertEqual(response.data['private'], False)
        self.assertEqual(response.data['default_member_rank'], -1)
        self.assertEqual(response.data['req_rank_invite'], Group.ADMINISTRATOR_RANK)

    #### Modification requests
    def test_update_school_unauthed(self):
        self.school_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_school_forbidden_1(self):
        self.client.force_authenticate(user=self.users[3])
        self.school_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_school_forbidden_2(self):
        self.client.force_authenticate(user=self.users[1])
        self.school_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_school_wrong_data(self):
        self.client.force_authenticate(user=self.users[2])
        self.school_data['name'] = ""
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_school_ok_staff(self):
        self.client.force_authenticate(user=self.users[2])
        self.school_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Ecole polytechnique")

    def test_update_school_ok_school_admin(self):
        self.client.force_authenticate(user=self.users[0])
        self.school_data['name'] = "Ecole polytechnique"
        response = self.client.put(self.school_url % self.school_data['id'], self.school_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Ecole polytechnique")

    #### Invitation process

    #### Deletion requests
