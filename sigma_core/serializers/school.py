from rest_framework import serializers

from sigma_core.models.school import School


class BasicSchoolSerializer(serializers.ModelSerializer):
    """
    Serialize School model without memberships.
    """
    class Meta:
        model = School


class SchoolSerializer(BasicSchoolSerializer):
    """
    Serialize School model with memberships.
    """
    class Meta:
        model = School

    subgroups = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    memberships = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
