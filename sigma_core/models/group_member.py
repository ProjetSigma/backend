from django.db import models
from django.http import Http404

from sigma_core.models.user import User

class GroupMember(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        unique_together = (("user", "group"),)

    user = models.ForeignKey('User', related_name='memberships')
    group = models.ForeignKey('Group', related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)
    is_accepted = models.BooleanField(default=False)

    # if super_administrator = True then is_administrator = True
    # administrators must have all the rights below
    is_administrator = models.BooleanField(default=False)
    is_super_administrator = models.BooleanField(default=False)
    can_invite = models.BooleanField(default=False)
    can_be_contacted = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)
    can_kick = models.BooleanField(default=False)
    can_modify_group_infos = models.BooleanField(default=False)

    # Related fields:
    #   - field_values (model GroupFieldValue)

    def __str__(self):
        return "User \"%s\" in Group \"%s\"" % (self.user.__str__(), self.group.__str__())

    # Perms for admin site
    def has_perm(self, perm, obj=None): # pragma: no cover
        return True

    def has_module_perms(self, app_label): # pragma: no cover
        return True
