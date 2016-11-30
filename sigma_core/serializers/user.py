from rest_framework import serializers
from sigma_core.models.group_member import GroupMember
from sigma_core.models.user import User
from sigma_core.models.group import Group

class UserSerializerMeta():
    model = User
    exclude = ('is_staff', 'is_superuser', 'invited_to_groups', 'groups', )
    read_only_fields = ('last_login', 'is_active', 'photo', )
    extra_kwargs = {'password': {'write_only': True, 'required': False}}


class MinimalUserSerializer(serializers.ModelSerializer):
    """
    Serialize an User with minimal data.
    """
    class Meta:
        model = User
        fields = ('id', 'lastname', 'firstname', 'is_active')
        read_only_fields = ('is_active', )


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize an User with related keys.
    """
    class Meta(UserSerializerMeta):
        pass


    def create(self, validated_data):
        return super().create(validated_data)


class MyUserSerializer(UserSerializer):
    """
    Serialize current User with related keys.
    """
    class Meta(UserSerializerMeta):
        pass

    invited_to_groups_ids = serializers.PrimaryKeyRelatedField(read_only=True, many=True, source='invited_to_groups')
