from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.group import BasicGroupSerializer
from sigma_core.serializers.user import BasicUserSerializer


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

class GroupMemberSerializer_WithUser(GroupMemberSerializer):
    user = BasicUserSerializer()

class GroupMemberSerializer_WithGroup(GroupMemberSerializer):
    group = BasicGroupSerializer()

class GroupMemberSerializer_WithUserAndGroup(GroupMemberSerializer):
    user = BasicUserSerializer()
    group = BasicGroupSerializer()
