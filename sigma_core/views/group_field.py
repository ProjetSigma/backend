from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field import GroupField
from sigma_core.serializers.group_field import GroupFieldSerializer, GroupFieldCreateSerializer


class GroupFieldViewSet(viewsets.ModelViewSet):
    queryset = GroupField.objects.all()
    serializer_class = GroupFieldSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_fields = ('name', )

    def create(self, request):
        serializer = GroupFieldCreateSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        mem = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
