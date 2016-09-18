from rest_framework import serializers

from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field import GroupField

class GroupMemberValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMemberValue
        read_only_fields = ('membership', 'field')

    membership = serializers.PrimaryKeyRelatedField(queryset=GroupMember.objects.all())
    field = serializers.PrimaryKeyRelatedField(queryset=GroupField.objects.all())

    def validate(self, fields):
        group_field = fields.get('field')
        mship = fields.get('membership')
        if group_field.group != mship.group:
            raise serializers.ValidationError("Condition (field.group == membership.group) is not verified.")
        GroupField.validate(group_field.type, group_field.accept, fields.get('value'))
        return super().validate(fields)
