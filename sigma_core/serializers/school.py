from rest_framework import serializers

from sigma_core.models.school import School


class BasicSchoolSerializer(serializers.ModelSerializer):
    """
    Serialize School model without memberships.
    """
    class Meta:
        model = School

    acknowledged_groups = serializers.PrimaryKeyRelatedField(read_only=True, many=True)


class SchoolSerializer(BasicSchoolSerializer):
    """
    Serialize School model with memberships.
    """
    class Meta:
        model = School

    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
