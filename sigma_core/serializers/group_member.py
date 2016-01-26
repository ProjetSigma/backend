from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        read_only_fields = ('perm_rank', )

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    def create(self, validated_data):
        mem = GroupMember(**validated_data)
        mem.perm_rank = mem.group.default_member_rank
        mem.save()
        return mem
