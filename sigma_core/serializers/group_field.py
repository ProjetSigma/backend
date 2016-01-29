from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group_field import GroupField
from sigma_core.models.group import Group

class GroupFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupField

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    validator_values = serializers.JSONField(binary=False)

class GroupFieldCreateSerializer(GroupFieldSerializer):
    class Meta:
        model = GroupField
    pass
