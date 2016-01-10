from django.http import Http404

from rest_framework import viewsets, decorators, status
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.user import User
from sigma_core.models.user_group import UserGroup
from sigma_core.serializers.user import BasicUserWithPermsSerializer, DetailedUserWithPermsSerializer
from sigma_core.serializers.user_group import UserGroupSerializer

class UserGroupViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ModelViewSet):
    permission_classes = (DRYPermissions, )
    queryset = User.objects.all()
    serializer_class = BasicUserWithPermsSerializer
    queryset_detail = queryset.prefetch_related('memberships__group')
    serializer_detail_class = DetailedUserWithPermsSerializer

    # decorators
    def require_group_member(func):
        def func_wrapper(self, request, pk=None, parent_lookup_memberships__group=None, *args, **kwargs):
            # Need to be authed
            if request.user.__class__.__name__ == 'AnonymousUser':
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # Need to be part of the group you want to see the members of
            user_group_relation = request.user.memberships.filter(group=parent_lookup_memberships__group)
            if (not user_group_relation or not user_group_relation[0].is_accepted()) and not request.user.is_sigma_admin():
                return Response(status=status.HTTP_403_FORBIDDEN)
            return func(self, request, pk, parent_lookup_memberships__group, *args, **kwargs)
        return func_wrapper

    # API calls
    @require_group_member
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)

    def create(self, request):
        pass

    @require_group_member
    def retrieve(self, request, pk, parent_lookup_memberships__group, *args, **kwargs):
        """
        Retrieve an User according to its id (pk).
        ---
        response_serializer: DetailedUserWithPermsSerializer
        """
        try:
            user = self.get_queryset(*args, **kwargs).get(pk=pk)
        except User.DoesNotExist:
            raise Http404()

        # Use DetailedUserWithPermsSerializer to have the groups whom user belongs to
        serializer = DetailedUserWithPermsSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        pass

    def partial_update(self, request, pk=None):
        pass

    def destroy(self, request, pk=None):
        pass
