from rest_framework import serializers

from sigma_core.models.validator import Validator

class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
    values = serializers.JSONField()
