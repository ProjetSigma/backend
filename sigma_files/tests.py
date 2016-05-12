import json
from PIL import Image as PIL_Image

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate

from sigma_core.tests.factories import UserFactory
from sigma_core.serializers.user import UserSerializer
from sigma_files.models import Image
from sigma_files.serializers import ImageSerializer


class ImageTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(ImageTests, self).setUpTestData()

        self.user = UserFactory()
        self.other_user = UserFactory()
        file = SimpleUploadedFile(name='test.jpg', content=PIL_Image.new('RGB', (15, 15)).tobytes(), content_type='image/jpeg')
        self.profile_image = Image.objects.create(file=file, owner=self.user)

        self.user.photo = self.profile_image
        self.user.save()

        serializer = ImageSerializer(self.profile_image)
        self.profile_data = serializer.data
        self.profiles_url = '/image/'
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

    def test_delete_forbidden(self):
        # Client wants to delete an image that he does not own
        self.client.force_authenticate(user=self.other_user)
        file = SimpleUploadedFile(name='test.jpg', content=PIL_Image.new('RGB', (15, 15)).tobytes(), content_type='image/jpeg')
        profile_image = Image.objects.create(file=file, owner=self.user)
        response = self.client.delete(self.profiles_url + "%d/" % profile_image.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ok(self):
        # Client wants to delete an image that he owns
        self.client.force_authenticate(user=self.user)
        file = SimpleUploadedFile(name='test.jpg', content=PIL_Image.new('RGB', (15, 15)).tobytes(), content_type='image/jpeg')
        profile_image = Image.objects.create(file=file, owner=self.user)
        response = self.client.delete(self.profiles_url + "%d/" % profile_image.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        try:
            img = Image.objects.get(pk=profile_image.id)
        except Image.DoesNotExist:
            img = None # File has been deleted
        self.assertEqual(img, None)
