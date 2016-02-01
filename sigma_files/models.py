import os.path

from django.db import models

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.user import User
from sigma_core.models.group import Group


class Image(models.Model):
    class Meta:
        abstract = True


def profile_img_path(instance, filename):
    from django.utils.crypto import get_random_string
    extension = os.path.splitext(filename)[1]
    return "img/profiles/" + get_random_string(length=150, allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_') + extension


class ProfileImage(Image):
    class Meta:
        pass

    file = models.ImageField(max_length=255, upload_to=profile_img_path)
    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Profile image of user %s" % self.user.__str__()

    def delete(self, *args, **kwargs):
        # TODO: Delete file
        return super(ProfileImage, self).delete(*args, **kwargs)

    # Permissions
