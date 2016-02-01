from rest_framework import serializers

from sigma_core.models.user import User
from sigma_core.models.group_field import GroupField
from sigma_core.models.group import Group
from sigma_core.models.validator import Validator

class GroupFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupField

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    validator_values = serializers.JSONField(binary=False)

    def validate(self, fields):
        validator = fields.get('validator')
        validator_fields = fields.get('validator_values')
        validator.validate_fields(validator_fields)
        return super().validate(fields)
