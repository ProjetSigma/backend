from django.http import Http404, HttpResponseForbidden

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field import GroupField
from sigma_core.serializers.group_field import GroupFieldSerializer, GroupFieldCreateSerializer

class GroupFieldViewSet(mixins.CreateModelMixin,    # Only Group admin
                   mixins.RetrieveModelMixin,       # Every Group member (including not accepted group members - for "open" groups)
                   mixins.UpdateModelMixin,         # Same permission as create
                   mixins.DestroyModelMixin,        # Same permission as create
                   mixins.ListModelMixin,           # Same permission as retrieve
                   viewsets.GenericViewSet):
    queryset = GroupField.objects.all()
    serializer_class = GroupFieldSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_fields = ('name', )

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
        serializer = GroupFieldCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.has_group_admin_perm(serializer.validated_data.get('group')):
            return Response('Not group administrator', status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
