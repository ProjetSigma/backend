from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.user import User
from sigma_core.models.group import Group


class Image(models.Model):
    class Meta:
        abstract = True


class ProfileImage(Image):
    class Meta:
        pass

    file = models.ImageField(max_length=255)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Profile image of user %s" % self.user.__str__()

    # Permissions
