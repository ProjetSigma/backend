from rest_framework import serializers

from sigma_files.models import ProfileImage


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage

    file = serializers.ImageField(max_length=255)
