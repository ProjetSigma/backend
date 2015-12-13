from rest_framework import serializers

from sigma_core.models.user_group import UserGroup


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup

    user = serializers.PrimaryKeyRelatedField()
    group = serializers.PrimaryKeyRelatedField()
