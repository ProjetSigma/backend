from rest_framework import serializers

from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.models.group import Group
from sigma_core.models.user import User

class GroupInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupInvitation

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    invitee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())