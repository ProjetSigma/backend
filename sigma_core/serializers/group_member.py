from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember


class GroupMemberSerializerMeta(object):
    model = GroupMember
    exclude = ('user', 'group', )
    read_only_fields = ('perm_rank', )


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta(GroupMemberSerializerMeta):
        pass

    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user')
    group_id = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(), source='group')

    def create(self, validated_data):
        mem = GroupMember(**validated_data)
        mem.perm_rank = mem.group.default_member_rank
        mem.save()
        return mem
