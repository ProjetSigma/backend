from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError
from django.db.models import Q

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.group_field import GroupField
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.serializers.group_member_value import GroupMemberValueSerializer

class GroupMemberValueViewSet(
        # You can only create a customfield for yourself
        # and you should be member of the group
        # and the group and customfield should match
        # ie membership.user = request.user && membership.group == field.group
                mixins.CreateModelMixin,
        # Only *accepted* group members can see other members custom fields
        # But you can always see your own custom fields
                mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,         # Only your own fields
                mixins.DestroyModelMixin,        # Only your own fields
                mixins.ListModelMixin,           # Same as "Retrieve"
                viewsets.GenericViewSet):
    queryset = GroupMemberValue.objects.all()
    available_memberships = GroupMember.objects.all()
    serializer_class = GroupMemberValueSerializer
    permission_classes = [IsAuthenticated, DRYPermissions, ]
    filter_fields = ('membership__user', 'membership__group', 'membership', 'field', 'value')

    # HERE we handle permissions filtering
    # You will never see fields for groups you are not a member of
    def get_queryset(self):
        from sigma_core.models.group_member import GroupMember
        if not self.request.user.is_authenticated():
            return self.queryset.none()
        if self.request.user.is_sigma_admin():
            return self.queryset
        # @sqlperf: Find which one is the most efficient
        my_groups = self.available_memberships.filter(user=self.request.user.id).filter(perm_rank__gte=1).values_list('group', flat=True)
        #my_groups = GroupMember.objects.filter(user=self.request.user.id)
        # But can always see your own custom fields
        return self.queryset.filter(Q(membership__group__in=my_groups) | Q(membership__user=self.request.user.id))

    def create(self, request):
        serializer = GroupMemberValueSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        mship = serializer.validated_data.get('membership')
        if mship.user != request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
