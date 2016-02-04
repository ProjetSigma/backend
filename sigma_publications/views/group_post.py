from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_member import GroupMember

from sigma_publications.models.group_post import GroupPost
from sigma_publications.serializers.group_post import GroupPostSerializer

class GroupPostViewSet(mixins.CreateModelMixin,    # TODO
                   mixins.RetrieveModelMixin,       # TODO
                   mixins.UpdateModelMixin,         # TODO
                   mixins.DestroyModelMixin,        # TODO
                   mixins.ListModelMixin,           # TODO
                   viewsets.GenericViewSet):
    queryset = GroupPost.objects.all()
    serializer_class = GroupPostSerializer
    permission_classes = [IsAuthenticated, ]

    # You will never see fields for groups you are not a member of
    def get_queryset(self):
        from sigma_core.models.group_member import GroupMember
        if not self.request.user.is_authenticated():
            return self.queryset.none()
        if self.request.user.is_sigma_admin():
            return self.queryset
        # @sqlperf: Find which one is the most efficient
        my_groups = GroupMember.objects.filter(user=self.request.user.id).values_list('group', flat=True)
        #my_groups = Group.objects.filter(memberships__user=self.request.user.id)
        return self.queryset.filter(group__in=my_groups)

    def create(self, request):
        serializer = GroupPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
