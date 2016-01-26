import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory, AdminUserFactory
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer


class UserTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(UserTests, self).setUpTestData()

        self.user = UserFactory()
        self.user2 = UserFactory()
        self.admin_user = AdminUserFactory()

        serializer = UserSerializer(self.user)
        self.user_data = serializer.data
        self.user_url = '/user/%d/' % self.user.id

        self.users_list = [self.user, self.user2, self.admin_user]

        self.new_user_data = {'lastname': 'Doe', 'firstname': 'John', 'email': 'john.doe@newschool.edu', 'password': 'password'}

#### List requests
    def test_get_users_list_unauthed(self):
        # Client not authenticated
        response = self.client.get('/user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_user_forbidden(self):
    #     # Client authenticated but has no permission
    #     self.client.force_authenticate(user=self.user2)
    #     response = self.client.get(self.user_url)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response.data.pop('permissions', None) # Workaround because DRY rest permissions needs a request
        self.assertEqual(response.data, self.user_data)

#### "Get my data" requests
    def test_get_my_data_unauthed(self):
        # Client is not authenticated
        response = self.client.get('/user/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_user_forbidden(self):
        # Client has no permission
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/user/', self.new_user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_ok(self):
        # Client has permissions
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/user/', self.new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['lastname'], self.new_user_data['lastname'])

#### Modification requests
    def test_edit_email_wrong_permission(self):
        # Client wants to change another user's email
        self.client.force_authenticate(user=self.user)
        user_data = UserSerializer(self.user2).data
        user_data['email'] = "pi@random.org"
        response = self.client.put("/user/%d/" % self.user2.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_is_superuser_no_permission(self):
        # Client can't set himself as administrator !
        self.client.force_authenticate(user=self.user)
        user_data = UserSerializer(self.user).data
        user_data['is_superuser'] = True
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertFalse(self.user.is_superuser);

    def test_edit_email_nonvalid_email(self):
        # Client wants to change his email with a non valid value
        self.client.force_authenticate(user=self.user)
        user_data = self.user_data.copy()
        user_data['email'] = "ThisIsNotAnEmail"
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_email_ok(self):
        # Client wants to change his email and succeed in
        self.client.force_authenticate(user=self.user)
        user_data = self.user_data.copy()
        user_data['email'] = "pi@random.org"
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user_data['email'])
        # Guarantee that tests are independant
        self.user.email = self.user_data['email']
        self.user.save()

    def test_edit_profile_wrong_permission(self):
        # Client wants to change another user's phone number
        self.client.force_authenticate(user=self.user)
        user_data = UserSerializer(self.user2).data
        user_data['phone'] = "0123456789"
        response = self.client.put("/user/%d/" % self.user2.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_profile_ok(self):
        # Client wants to change his phone number
        self.client.force_authenticate(user=self.user)
        user_data = self.user_data.copy()
        user_data['phone'] = "0123456789"
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], user_data['phone'])
        # Guarantee that tests are independant
        self.user.phone = self.user_data['phone']
        self.user.save()

    def test_edit_lastname_wrong_permission(self):
        # Client wants to change his lastname
        self.client.force_authenticate(user=self.user)
        user_data = self.user_data.copy()
        user_data['lastname'] = "Daudet"
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_edit_lastname_ok(self):
        # Admin wants to change an user's lastname
        self.client.force_authenticate(user=self.admin_user)
        user_data = self.user_data.copy()
        user_data['lastname'] = "Daudet"
        response = self.client.put("/user/%d/" % self.user.id, user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lastname'], user_data['lastname'])
        # Guarantee that tests are independant
        self.user.lastname = self.user_data['lastname']
        self.user.save()


#### "Change password" requests
    def test_change_pwd_wrong_pwd(self):
        # Client gives a wrong old password
        self.user.set_password('old_pwd')
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/user/change_password/', {'old_password': 'wrong', 'password': 'new_pwd'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_pwd_no_pwd(self):
        # Client gives no new password
        self.user.set_password('old_pwd')
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/user/change_password/', {'old_password': 'old_pwd', 'password': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_pwd_ok(self):
        # Client successfully changes his password
        self.user.set_password('old_pwd')
        self.client.force_authenticate(user=self.user)
        response = self.client.put('/user/change_password/', {'old_password': 'old_pwd', 'password': 'new_strong_pwd'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

#### "Reset password" requests
    def test_reset_pwd_no_email(self):
        # Client gives no email
        response = self.client.post('/user/reset_password/', {'email': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_pwd_no_user(self):
        # Client's email is not found
        response = self.client.post('/user/reset_password/', {'email': 'unknown@email.me'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_reset_pwd_ok(self):
        # Client successfully resets his password
        response = self.client.post('/user/reset_password/', {'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        from sigma_core.views.user import reset_mail
        self.assertEqual(mail.outbox[0].subject, reset_mail['subject'])

#### Deletion requests
