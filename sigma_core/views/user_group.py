from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin

from sigma_core.models.user import User
from sigma_core.models.user_group import UserGroup
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer
from sigma_core.serializers.user_group import UserGroupSerializer


class UserGroupViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = BasicUserWithPermsSerializer
    queryset_detail = User.objects.all().prefetch_related('memberships__group')
    serializer_detail_class = DetailedUserWithPermsSerializer

    # TODO: write the views to manage UserGroup relations
