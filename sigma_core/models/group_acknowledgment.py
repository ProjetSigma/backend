from django.db import models
from sigma_core.models.group import Group

class GroupAcknowledgment(models.Model):
    subgroup = models.ForeignKey(Group, related_name='group_parents')
    parent_group = models.ForeignKey(Group, related_name='subgroups')
    validated = models.BooleanField(default=False)
    delegate_admin = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self): # pragma: no cover
        if self.validated:
            return "Group %s acknowledged by Group %s" % (self.subgroup.__str__(), self.parent_group.__str__())
        else:
            return "Group %s awaiting for acknowledgment by Group %s since %s" % (self.subgroup.__str__(), self.parent_group.__str__(), self.created.strftime("%Y-%m-%d %H:%M"))
