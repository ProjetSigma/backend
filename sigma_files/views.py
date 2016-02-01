from django.http import Http404

from rest_framework import viewsets, decorators, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sigma_files.models import ProfileImage
from sigma_files.serializers import ProfileImageSerializer


class ProfileImageViewSet(viewsets.ModelViewSet):
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated, ]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, ]
    
