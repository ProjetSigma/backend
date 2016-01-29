from django.http import Http404

from rest_framework import viewsets, decorators, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dry_rest_permissions.generics import DRYPermissions

from sigma_core.models.validator import Validator
from sigma_core.serializers.validator import ValidatorSerializer


class ValidatorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Validator.objects.all()
    serializer_class = ValidatorSerializer
    filter_fields = ('display_name', 'html_name')
    permission_classes = []
