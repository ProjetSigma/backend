from django.db import models

from sigma_core.models.custom_field import CustomField
from sigma_core.models.user import User

class GroupMemberValue(models.Model):
    class Meta:
        unique_together = (("membership", "field"),)

    membership = models.ForeignKey('GroupMember', related_name='values')
    field = models.ForeignKey('GroupField', related_name='+')
    value = models.CharField(max_length=CustomField.FIELD_VALUE_MAX_LENGTH)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return request.user.is_authenticated()

    # Object-level permissions are handled on GroupMemberValueViewSet
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return request.user.is_authenticated()

    def has_object_write_permission(self, request):
        return request.user.is_authenticated() and self.membership.user == request.user
