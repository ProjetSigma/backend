from django.db import models


class Group(models.Model):
    class Meta:
        pass

    VIS_PUBLIC = 0
    VIS_PRIVATE = 1
    VISIBILITY_CHOICES = (
        (VIS_PUBLIC, 'PUBLIC'),
        (VIS_PRIVATE, 'PRIVATE')
    )

    MEMBER_ANYONE = 0
    MEMBER_REQUEST = 1
    MEMBER_INVITATION = 2
    MEMBERSHIP_CHOICES = (
        (MEMBER_ANYONE, 'ANYONE'),
        (MEMBER_REQUEST, 'REQUEST'),
        (MEMBER_INVITATION, 'INVITATION')
    )

    VALID_ADMINS = 0
    VALID_MEMBERS = 1
    VALIDATION_CHOICES = (
        (VALID_ADMINS, 'ADMINS'),
        (VALID_MEMBERS, 'MEMBERS')
    )

    TYPE_BASIC = 0
    TYPE_CURSUS = 1
    TYPE_ASSO = 2
    TYPE_PROMO = 3
    TYPE_SCHOOL = 4
    TYPE_CHOICES = (
        (TYPE_BASIC, 'BASIC'),
        (TYPE_CURSUS, 'CURSUS/DEPARTMENT'),
        (TYPE_ASSO, 'ASSOCIATION'),
        (TYPE_PROMO, 'PROMOTION'),
        (TYPE_SCHOOL, 'SCHOOL')
    )

    name = models.CharField(max_length=254)
    visibility = models.SmallIntegerField(choices=VISIBILITY_CHOICES, default=VIS_PRIVATE)
    membership_policy = models.SmallIntegerField(choices=MEMBERSHIP_CHOICES, default=MEMBER_INVITATION)
    validation_policy = models.SmallIntegerField(choices=VALIDATION_CHOICES, default=VALID_ADMINS)
    type = models.SmallIntegerField(choices=TYPE_CHOICES, default=TYPE_BASIC)

    def __str__(self):
        return "%s (%s)" % (self.name, self.get_type_display())
