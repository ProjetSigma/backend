from django.db import models


class Group(models.Model):
    class Meta:
        pass

    GROUP_MAXIMUM_RANK  = 10

    VIS_PUBLIC          = 'public'
    VIS_PRIVATE         = 'private'
    VISIBILITY_CHOICES = (
        (VIS_PUBLIC, 'Anyone can see the group'),
        (VIS_PRIVATE, 'Group is not visible')
    )

    TYPE_BASIC          = 'basic'
    TYPE_CURSUS         = 'cursus'
    TYPE_ASSO           = 'association'
    TYPE_PROMO          = 'school_promotion'
    TYPE_SCHOOL         = 'school'
    TYPE_CHOICES = (
        (TYPE_BASIC, 'Simple group'),
        (TYPE_CURSUS, 'Cursus or department'),
        (TYPE_ASSO, 'Association'),
        (TYPE_PROMO, 'School promotion'),
        (TYPE_SCHOOL, 'School')
    )

    name = models.CharField(max_length=254)
    visibility = models.CharField(max_length=64, choices=VISIBILITY_CHOICES, default=VIS_PRIVATE)
    type = models.CharField(max_length=64, choices=TYPE_CHOICES, default=TYPE_BASIC)

    # The permission a member has upon joining
    # A value of -1 means that no one can join the group.
    # A value of 0 means that anyone can request to join the group
    default_member_rank = models.SmallIntegerField(default=-1)
    # Invite new members on the group
    req_rank_invite = models.SmallIntegerField(default=1)
    # Remove a member from the group
    req_rank_kick = models.SmallIntegerField(default=GROUP_MAXIMUM_RANK)
    # Upgrade someone rank 0 to rank 1
    req_rank_accept_join_requests = models.SmallIntegerField(default=1)
    # Upgrade other users (up to $yourRank - 1)
    req_rank_promote = models.SmallIntegerField(default=GROUP_MAXIMUM_RANK)
    # Downgrade someone (to rank 1 minimum)
    req_rank_demote = models.SmallIntegerField(default=GROUP_MAXIMUM_RANK)
    # Modify group description
    req_rank_modify_group_infos = models.SmallIntegerField(default=GROUP_MAXIMUM_RANK)

    # Related fields:
    #   - invited_users (model User)

    def can_anyone_join(self):
        return default_member_rank >= 0
    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())
