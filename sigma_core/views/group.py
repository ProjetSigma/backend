from rest_framework import viewsets, decorators, status
from rest_framework.response import Response

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
