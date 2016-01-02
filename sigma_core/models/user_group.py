from django.db import models

from sigma_core.models.user import User
from sigma_core.models.group import Group


class UserGroup(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        pass

    user = models.ForeignKey(User, related_name='memberships')
    group = models.ForeignKey(Group, related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "User \"%s\" in Group \"%s\"" % (self.user.__str__(), self.group.__str__())
