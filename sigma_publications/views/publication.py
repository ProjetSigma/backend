from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError, PermissionDenied

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_publications.models import Publication
from sigma_publications.serializers import PublicationSerializer

from django.db.models import F

class PublicationViewSet(mixins.CreateModelMixin,   # Everyone can create a publication
                   #mixins.RetrieveModelMixin,      # Not needed. Will be retrieved with the GroupPost view
                                                    # TODO: Maybe for sigma admins, to see where it is posted ?
                   mixins.UpdateModelMixin,         # Only your own Publication
                   mixins.DestroyModelMixin,        # Only if it is not posted already, or for sigma admins
                   #mixins.ListModelMixin,          # Not needed. Will be retrieved with the GroupPost view
                   viewsets.GenericViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        """
        Create a new Publication. Only visible by the user at first.
        """
        serializer = self.get_serializer(data=request.data)
        allowed_groups = Group.objects.filter(memberships__user=request.user,
            memberships__perm_rank__gte=F('req_rank_create_group_publication'))
        serializer.fields['poster_group'] = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=allowed_groups)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update the Publication text. The autor User or autor Group are not modifiable.
        """
        if not request.user.is_sigma_admin():
            self.queryset = self.queryset.filter(poster_user=request.user)
        return super().update(request, *args, **kwargs)

    def check_object_permissions(self, request, publication):
        if self.action == "destroy":
            if publication.comments.all():
                raise PermissionDenied()
            if publication.posts.all():
                raise PermissionDenied()
        return super().check_object_permissions(request, publication)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy the Publication.
        Only possible if there is no comment and if the publication is not already posted.
        """
        if not request.user.is_sigma_admin():
            self.queryset = self.queryset.filter(poster_user=request.user)
        return super().destroy(request, *args, **kwargs)
