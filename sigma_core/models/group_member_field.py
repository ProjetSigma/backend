from django.db import models

from sigma_core.models.custom_field import CustomField
from sigma_core.models.user import User

class GroupMemberField(models.Model):
    class Meta:
        unique_together = (("membership", "field"),)

    membership = models.ForeignKey('GroupMember', related_name='values')
    fields = models.ForeignKey('GroupField', related_name='+')
    value = models.CharField(max_length=CustomField.FIELD_VALUE_MAX_LENGTH)

    def has_object_read_permission(self, request):
        return self.membership.user.is_group_member(self.membership.group)
    def has_object_write_permission(self, request):
        return self.membership.user.is_group_member(self.membership.group) and self.membership.user == request.user
