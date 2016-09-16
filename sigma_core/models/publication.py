from django.db import models

from sigma_core.models.group import Group
from sigma_core.models.event import Event


class Publication(models.Model):

    ##########
    # Fields #
    ##########

    content = models.CharField(max_length=1400)
    group = models.ForeignKey(Group, related_name='group')
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)
    related_event = models.ForeignKey(Event, blank=True)
    internal = models.BooleanField(default=True)
    last_commented = models.DateTimeField(auto_now_add=True)
