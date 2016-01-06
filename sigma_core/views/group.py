from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from sigma_core.models.group import Group
from sigma_core.serializers.group import GroupSerializer


class GroupViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
