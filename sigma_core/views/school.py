from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.school import School
from sigma_core.serializers.school import SchoolSerializer


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny, ]

        return super(SchoolViewSet, self).get_permissions()
