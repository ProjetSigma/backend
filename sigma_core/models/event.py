from django.db import models

from sigma_core.models.group import Group
from sigma_core.models.publication import Publication


class Event(models.Model):

    ##########
    # Fields #
    ##########

    name = models.CharField(max_length=140)
    related_publication = models.ForeignKey(Publication, related_name='publication')
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    description = models.CharField(max_length=1400)
    place_name = models.CharField(max_length=140)
    # ToDo : place_localisation
