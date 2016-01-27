from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.group import Group


class School(Group):
    design = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """
        Schools are special groups: some params cannot be specified by user.
        """
        self.visibility = Group.VIS_PUBLIC
        self.type = Group.TYPE_SCHOOL
        self.default_member_rank = -1
        self.req_rank_invite = Group.ADMINISTRATOR_RANK
        self.req_rank_kick = Group.ADMINISTRATOR_RANK
        self.req_rank_accept_join_requests = Group.ADMINISTRATOR_RANK
        self.req_rank_promote = Group.ADMINISTRATOR_RANK
        self.req_rank_demote = Group.ADMINISTRATOR_RANK
        self.req_rank_modify_group_infos = Group.ADMINISTRATOR_RANK

        return super(School, self).save(*args, **kwargs)

    # Permissions
    @staticmethod
    def has_read_permission(request):
        """
        Schools list is visible by everybody.
        """
        return True

    def has_object_read_permission(self, request):
        """
        Schools are only visible by members.
        """
        return request.user.is_group_member(self)

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        """
        Schools can be created by Sigma admin only.
        """
        return False
