from django.db import models

from sigma_core.models.group import Group

class Event(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################

    ################################################################
    # FIELDS                                                       #
    ################################################################

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1400)

    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    place_name = models.CharField(max_length=255)
    # ToDo : place_localisation

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
