from rest_framework import serializers

from sigma_files.models import ProfileImage


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage

    file = serializers.ImageField(max_length=255)
    height = serializers.IntegerField(source='file.height', read_only=True)
    width = serializers.IntegerField(source='file.width', read_only=True)
