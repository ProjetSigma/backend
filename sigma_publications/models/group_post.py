from django.db import models

from sigma_core.models.group import Group
from sigma_publications.models.publication import Publication

class GroupPost(models.Model):
    """
    Modelize a Post on a Group. A Post is a link between a Publication and a Group.
    """
    class Meta:
        pass

    # Poster ?
    group = models.ForeignKey(Group, related_name='posts', on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, related_name='posts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
