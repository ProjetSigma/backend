from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer, DetailedUserSerializer

class GroupUserViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = DetailedUserSerializer
    queryset_detail = queryset
    serializer_detail_class = DetailedUserWithPermsSerializer

    # Decorators
    def require_group_member(func):
        """
        Let the user see the data if he is member of the requested group or if he is admin.
        """
        def func_wrapper(self, request, parent_lookup_memberships__group=None, *args, **kwargs):
            # Need to be authed
            if request.user.__class__.__name__ == 'AnonymousUser':
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Need to be part of the group you want to see the members of
            if not request.user.is_sigma_admin() and not request.user.is_group_member(parent_lookup_memberships__group):
                parent_lookup_memberships__group = None
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
