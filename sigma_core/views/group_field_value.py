from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field_value import GroupFieldValue
from sigma_core.serializers.group_field_value import GroupFieldValueSerializer

class GroupFieldValueViewSet(viewsets.ModelViewSet):
    queryset = GroupFieldValue.objects.all()
    serializer_class = GroupFieldValueSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    

