from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.user_group import UserGroup
from sigma_core.serializers.group import BasicGroupSerializer


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        read_only_fields = ('perm_rank', )

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = BasicGroupSerializer()
