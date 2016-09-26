from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.serializers.group_field import GroupFieldSerializer
from sigma_core.models.group_field import GroupField

class GroupFieldViewSet(viewsets.ModelViewSet):
    queryset = GroupField.objects.all()
    serializer_class = GroupFieldSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]