from django.db import models

from sigma_core.models.group import Group
from sigma_core.models.event import Event
from sigma_core.models.user import User

class Publication(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################

    ################################################################
    # FIELDS                                                       #
    ################################################################

    group = models.ForeignKey(Group, related_name='publications')
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User)

    name = models.CharField(max_length=1500)
    content = models.CharField(max_length=1500)

    related_event = models.ForeignKey(Event, blank=True)
    internal = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    last_commented = models.DateTimeField(auto_now_add=True)

    ################################################################
    # PERMISSIONS                                                  #
    ################################################################

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_write_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    def __str__(self):
        return self.name
