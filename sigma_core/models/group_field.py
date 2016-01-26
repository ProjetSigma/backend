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
        return request.user.is_authenticated()

    def has_object_read_permission(self, request):
        return request.user.is_authenticated() and request.user.is_group_member(self.group)

    @staticmethod
    def has_write_permission(request):
        return request.user.is_authenticated()

    def has_object_write_permission(self, request):
        return request.user.is_authenticated() and request.user.is_group_admin(self.group)
