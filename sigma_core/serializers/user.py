from rest_framework import serializers
from dry_rest_permissions.generics import DRYPermissionsField

from sigma_core.models.user import User
from sigma_core.serializers.user_group import UserGroupSerializer


class BasicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}


class BasicUserWithPermsSerializer(BasicUserSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    permissions = DRYPermissionsField(read_only=True)


class DetailedUserSerializer(BasicUserSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    memberships = UserGroupSerializer(read_only=True, many=True)


class DetailedUserWithPermsSerializer(DetailedUserSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True, 'required': False}}

    permissions = DRYPermissionsField(read_only=True)
