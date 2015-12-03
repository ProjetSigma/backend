import factory
import json

from django.utils.text import slugify

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from sigma_core.models.user import User, UserSerializer

# Factories
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    lastname = factory.Faker('last_name')
    firstname = factory.Faker('first_name')
    email = factory.LazyAttribute(lambda obj: '%s.%s@school.edu' % (slugify(obj.firstname), slugify(obj.lastname)))

class AdminUserFactory(UserFactory):
    is_staff = True


# Tests for User management
class UserTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(UserTests, self).setUpTestData()

        self.user = UserFactory()
        self.admin_user = AdminUserFactory()

        serializer = UserSerializer(self.user)
        self.user_data = serializer.data
        self.user_url = '/user/%d/' % self.user.id

        self.users_list = [self.user, self.admin_user]

        self.new_user_data = {'lastname': 'Doe', 'firstname': 'John', 'email': 'john.doe@newschool.edu', 'password': 'password'}

    #### List requests
    def test_get_users_list_unauthed(self):
        # Client not authenticated
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_get_users_list_forbidden(self):
    #     # Client authenticated but has no permission
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.get('/user/')
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_users_list_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.users_list))

    #### Get requests
    def test_get_user_unauthed(self):
        # Client is not authenticated
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_get_user_forbidden(self):
    #     response = self.client.get(self.user_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.user_data)

    #### "Get my data" requests
    def test_get_my_data_unauthed(self):
        # Client is not authenticated
        response = self.client.get('/user/me/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_my_data_ok(self):
        # Client is authenticated
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/user/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)

    #### Create requests
    def test_create_user_unauthed(self):
        # Client is not authenticated
        response = self.client.post('/user/', self.new_user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_create_user_forbidden(self):
    #     # Client has no permission
    #     self.client.force_authenticate(user=self.user)
    #     response = self.client.post('/user/', self.new_user_data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/user/', self.new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['lastname'], self.new_user_data['lastname'])

    #### Modification requests

    #### "Change password" requests

    #### Deletion requests
