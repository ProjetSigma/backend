from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma_core.models.user import User


class UserWithoutPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


class UserSerializer(UserWithoutPermissionsSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    permissions = DRYPermissionsField(read_only=True)
