from django.db import models

from sigma_core.models.user import User
from sigma_core.models.event import Event

class Participation(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################

    POSSIBLE_STATUS = (
        (0, 'Invited'),
        (1, 'Interested'),
        (2, 'Participates'),
    )

    ################################################################
    # FIELDS                                                       #
    ################################################################

    user = models.ForeignKey(User)
    event = models.ForeignKey(Event)
    status = models.IntegerField(choices=POSSIBLE_STATUS)

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
        return self.user.firstname
