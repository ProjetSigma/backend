import json
from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory
from sigma_core.serializers.user import DetailedUserSerializer as UserSerializer
from sigma_files.models import ProfileImage
from sigma_files.serializers import ProfileImageSerializer


class ProfileImageTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(ProfileImageTests, self).setUpTestData()

        self.user = UserFactory()
        file = SimpleUploadedFile(name='test.jpg', content=Image.new('RGB', (15, 15)).tobytes(), content_type='image/jpeg')
        self.profile_image = ProfileImage.objects.create(file=file)

        self.user.photo = self.profile_image
        self.user.save()

        serializer = ProfileImageSerializer(self.profile_image)
        self.profile_data = serializer.data
        self.profiles_url = '/profile-image/'
        self.profile_url = self.profiles_url + '%d/' % self.profile_image.id

    def test_get_list_unauthed(self):
        # Client not authenticated
        response = self.client.get(self.profiles_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_list_ok(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profiles_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_one_ok(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_unauthed(self):
        with open("sigma_files/test_img.png", "rb") as img:
             response = self.client.post(self.profiles_url, {'file': img}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_ok(self):
        self.client.force_authenticate(user=self.user)
        with open("sigma_files/test_img.png", "rb") as img:
             response = self.client.post(self.profiles_url, {'file': img}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
