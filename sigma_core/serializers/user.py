from rest_framework import serializers

from sigma_core.models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('is_staff', 'is_superuser', )
        read_only_fields = ('last_login', 'is_active', )
        extra_kwargs = {'password': {'write_only': True}}
