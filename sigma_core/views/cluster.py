from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from sigma_core.models.cluster import Cluster
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.cluster import BasicClusterSerializer, ClusterSerializer


class ClusterViewSet(mixins.CreateModelMixin,   # Only sigma admins
                    mixins.ListModelMixin,      # Everyone (even if not authed)
                    mixins.RetrieveModelMixin,  # Everyone (even if not authed)
                    mixins.UpdateModelMixin,    # Only sigma admins
                    mixins.DestroyModelMixin,   # ??
                    viewsets.GenericViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = [IsAuthenticated, ]

    def only_staff(func):
        def func_wrapper(self, request, *args, **kwargs):
            if not request.user.is_authenticated() or not request.user.is_sigma_admin():
                return Response(status=status.HTTP_403_FORBIDDEN)
            return func(self, request, *args, **kwargs)
        return func_wrapper

    def restrict_queryset_to_administrated_clusters(func):
        def func_wrapper(self, request, *args, **kwargs):
            if not request.user.is_sigma_admin():
                self.queryset = self.queryset.filter(pk__in=GroupMember.objects.filter(user=request.user, perm_rank=Group.ADMINISTRATOR_RANK).values_list('group', flat=True))
            return func(self, request, *args, **kwargs)
        return func_wrapper

    @only_staff
    def create(self, request):
        return super().create(request)

    @restrict_queryset_to_administrated_clusters
    def update(self, request, pk=None):
        return super().update(request, pk=pk)

    @only_staff
    def destroy(self, request, pk=None):
        return super().destroy(request, pk=pk)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return BasicClusterSerializer
        return super().get_serializer_class()
