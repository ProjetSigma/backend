from django.db import models

from sigma_core.models.user import User
from sigma_core.models.group import Group


class UserGroup(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        # TODO: Make a primary key once Django supports it
        unique_together = (("user", "group"),)

    user = models.ForeignKey(User, related_name='memberships')
    group = models.ForeignKey(Group, related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)
    perm_rank = models.SmallIntegerField(blank=False, default=1)

    def can_invite(self):
        return self.perm_rank >= self.group.req_rank_invite
    def can_kick(self):
        return self.perm_rank >= self.group.req_rank_kick

    def is_accepted(self):
        return self.perm_rank > 0
    def __str__(self):
        return "User \"%s\" r%d in Group \"%s\"" % (self.user.__str__(), self.perm_rank, self.group.__str__())
