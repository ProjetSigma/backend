from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field import GroupField
from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.serializers.group_member_value import GroupMemberValueSerializer

class GroupMemberValueViewSet(mixins.CreateModelMixin,    # TODO
                   mixins.RetrieveModelMixin,       # TODO
                   mixins.UpdateModelMixin,         # TODO
                   mixins.DestroyModelMixin,        # TODO
                   mixins.ListModelMixin,           # TODO
                   viewsets.GenericViewSet):
    queryset = GroupMemberValue.objects.all()
    serializer_class = GroupMemberValueSerializer
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
        my_groups = GroupMember.objects.filter(user=self.request.user.id).values_list('pk', flat=True)
        #my_groups = GroupMember.objects.filter(user=self.request.user.id)
        return self.queryset.filter(membership__in=my_groups)


    def create(self, request):
        serializer = GroupMemberValueSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        mship = serializer.validated_data.get('membership')
        if mship.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
