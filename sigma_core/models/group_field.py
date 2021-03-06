from django.db import models

from sigma_core.models.custom_field import CustomField


class GroupField(CustomField):
    class Meta:
        pass

    group = models.ForeignKey('Group', related_name='fields')
    # Generated fields:
    #   values

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    @staticmethod
    def has_read_permission(request):
        return True

    # Object-level permissions are handled on GroupFieldViewSet
    #def has_object_read_permission(self, request):
    #    return request.user.is_group_member(self.group)

    @staticmethod
    def has_write_permission(request):
        return True

    def has_object_write_permission(self, request):
        return request.user.has_group_admin_perm(self.group)
