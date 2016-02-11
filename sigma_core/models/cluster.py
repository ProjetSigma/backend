from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.group import Group


class Cluster(Group):
    design = models.CharField(max_length=255)

    DEFAULT_MEMBER_RANK = 1

    # Related fields:
    #   - cluster_users (model User.clusters)

    def save(self, *args, **kwargs):
        """
        Clusters are special groups: some params cannot be specified by user.
        """
        self.private = False
        self.default_member_rank = -1
        self.req_rank_invite = Group.ADMINISTRATOR_RANK
        self.req_rank_kick = Group.ADMINISTRATOR_RANK
        self.req_rank_accept_join_requests = Group.ADMINISTRATOR_RANK
        self.req_rank_promote = Group.ADMINISTRATOR_RANK
        self.req_rank_demote = Group.ADMINISTRATOR_RANK
        self.req_rank_modify_group_infos = Group.ADMINISTRATOR_RANK
        self.resp_cluster = None
        self.protected = True

        return super().save(*args, **kwargs)
