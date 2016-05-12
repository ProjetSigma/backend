from django.http import Http404

from rest_framework import viewsets, decorators, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sigma_files.models import Image
from sigma_files.serializers import ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, ]
