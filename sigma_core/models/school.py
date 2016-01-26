from django.db import models

from sigma_core.models.group import Group


class School(Group):
    design = models.CharField(max_length=255)
