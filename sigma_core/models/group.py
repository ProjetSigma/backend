from django.db import models


class Group(models.Model):
    class Meta:
        pass

    VIS_PUBLIC          = 'public'
    VIS_PRIVATE         = 'private'
    VISIBILITY_CHOICES = (
        (VIS_PUBLIC, 'Anyone can see the group'),
        (VIS_PRIVATE, 'Group is not visible')
    )

    MEMBER_ANYONE       = 'anyone'
    MEMBER_REQUEST      = 'request'
    MEMBER_INVITATION   = 'upon_invitation'
    MEMBERSHIP_CHOICES = (
        (MEMBER_ANYONE, 'Anyone can join the group'),
        (MEMBER_REQUEST, 'Anyone can request to join the group'),
        (MEMBER_INVITATION, 'Can join the group only upon invitation')
    )

    VALID_ADMINS        = 'admins'
    VALID_MEMBERS       = 'members'
    VALIDATION_CHOICES = (
        (VALID_ADMINS, 'Only admins can accept join requests or invite members'),
        (VALID_MEMBERS, 'Every member can accept join requests or invite members')
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
    visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICES, default=VIS_PRIVATE)
    membership_policy = models.SmallIntegerField(choices=MEMBERSHIP_CHOICES, default=MEMBER_INVITATION)
    validation_policy = models.SmallIntegerField(choices=VALIDATION_CHOICES, default=VALID_ADMINS)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_BASIC)

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())
