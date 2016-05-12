from django.db import models
from django.http import Http404

from sigma_core.models.user import User

class GroupMember(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        # TODO: Make a primary key once Django supports it
        unique_together = (("user", "group"),)

    user = models.ForeignKey('User', related_name='memberships')
    group = models.ForeignKey('Group', related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)
    perm_rank = models.SmallIntegerField(blank=False, default=1)

    # Related fields:
    #   - values (model GroupMemberValue)

    def can_invite(self):
        return self.perm_rank >= self.group.req_rank_invite

    def can_kick(self):
        return self.perm_rank >= self.group.req_rank_kick

    def is_accepted(self):
        return self.perm_rank > 0

    def __str__(self): # pragma: no cover
        return "User \"%s\" r%d in Group \"%s\"" % (self.user.__str__(), self.perm_rank, self.group.__str__())

    # Perms for admin site
    def has_perm(self, perm, obj=None): # pragma: no cover
        return True

    def has_module_perms(self, app_label): # pragma: no cover
        return True
