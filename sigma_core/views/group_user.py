from django.http import Http404
try:
    from django.utils import six
except ImportError:
    from rest_framework import six

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.user_group import UserGroup
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer, DetailedUserSerializer
from sigma_core.serializers.user_group import UserGroupSerializer

class GroupUserViewSet(NestedViewSetMixin,
                    DetailSerializerMixin,
                    #mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    #mixins.UpdateModelMixin,
                    #mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = DetailedUserSerializer
    queryset_detail = queryset
    serializer_detail_class = DetailedUserWithPermsSerializer

    # Decorators
    def require_group_member(func):
        def func_wrapper(self, request, parent_lookup_memberships__group=None, *args, **kwargs):
            # Need to be authed
            #import pdb; pdb.set_trace()
            if request.user.__class__.__name__ == 'AnonymousUser':
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Need to be part of the group you want to see the members of
            if not request.user.is_sigma_admin() and not request.user.is_group_member(parent_lookup_memberships__group):
                return Response(status=status.HTTP_403_FORBIDDEN)
            return func(self, request, group=parent_lookup_memberships__group, *args, **kwargs)
        return func_wrapper

    # Restful API
    @require_group_member
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    @require_group_member
    def retrieve(self, request, pk, group, *args, **kwargs):
        """
        Retrieve an User according to its id (pk).
        ---
        response_serializer: DetailedUserWithPermsSerializer
        """
        try:
            user = self.queryset.filter(pk=pk).get(memberships__group=group)
        except User.DoesNotExist:
            raise Http404()

        # Use DetailedUserWithPermsSerializer to have the groups whom user belongs to
        serializer = DetailedUserWithPermsSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
