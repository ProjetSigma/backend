from django.http import Http404, HttpResponseForbidden
from django.core.exceptions import ValidationError

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sigma_publications.models import Publication
from sigma_publications.serializers.publication import PublicationSerializer

class PublicationViewSet(mixins.CreateModelMixin,    # TODO
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
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
