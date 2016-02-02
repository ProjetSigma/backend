from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma.utils import CurrentUserCreateOnlyDefault
from sigma_files.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image

    file = serializers.ImageField(max_length=255)
    height = serializers.IntegerField(source='file.height', read_only=True)
    width = serializers.IntegerField(source='file.width', read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=CurrentUserCreateOnlyDefault())
    permissions = DRYPermissionsField(actions=['read', 'write'])
