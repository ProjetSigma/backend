from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from sigma_core.models.group import Group
from sigma_publications.models import Publication
from sigma_publications.serializers import PublicationSerializer

from django.db.models import F

class PublicationViewSet(mixins.CreateModelMixin,    # Everyone can create a publication
                   #mixins.RetrieveModelMixin,       # TODO?
                   mixins.UpdateModelMixin,         # TODO
                   mixins.DestroyModelMixin,        # TODO
                   #mixins.ListModelMixin,           # TODO?
                   viewsets.GenericViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request):
        serializer = PublicationSerializer(data=request.data)

        allowed_groups = Group.objects.filter(memberships__user=request.user,
            memberships__perm_rank__gte=F('req_rank_create_group_publication'))
        serializer.fields['poster_group'] = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=allowed_groups)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data.get('poster_user').id != request.user.id:
            return Response("`poster_user` should be yourself", status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
