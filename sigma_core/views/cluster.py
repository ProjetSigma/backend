from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.cluster import Cluster
from sigma_core.serializers.cluster import BasicClusterSerializer, ClusterSerializer


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return BasicClusterSerializer
        return super().get_serializer_class()

    
