from django.db import models

from sigma_core.models.group import Group


class Cluster(Group):
    design = models.CharField(max_length=255)


    # Related fields:
    #   - cluster_users (model User.clusters)

    def save(self, *args, **kwargs):
        """
        Clusters are special groups: some params cannot be specified by user.
        """
        self.is_private = False
        self.is_protected = True
        self.can_anyone_join = False

        return super().save(*args, **kwargs)

    @property
    def subgroups_list(self):
        return self.group_ptr.subgroups_list
