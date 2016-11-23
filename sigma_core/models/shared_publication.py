from django.db import models

from sigma_core.models.publication import Publication
from sigma_core.models.group import Group

class SharedPublication(models.Model):

    ################################################################
    # CONSTANTS                                                    #
    ################################################################

    # Liste des champs de l'objet
    publication = models.ForeignKey(Publication, related_name='shared')
    group = models.ForeignKey(Group, related_name='shared_publications')
    approved = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

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
        return self.publication.name
