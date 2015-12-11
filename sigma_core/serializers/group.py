from rest_framework import serializers

from sigma_core.models.group import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group

    visibility = serializers.SerializerMethodField()
    membership_policy = serializers.SerializerMethodField()
    validation_policy = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    def get_visibility(self, obj):
        return obj.get_visibility_display()

    def get_membership_policy(self, obj):
        return obj.get_membership_policy_display()

    def get_validation_policy(self, obj):
        return obj.get_validation_policy_display()

    def get_type(self, obj):
        return obj.get_type_display()
