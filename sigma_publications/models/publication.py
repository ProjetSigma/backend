from django.db import models

from sigma_core.models.group import Group
from sigma_core.models.user import User

class Publication(models.Model):
    """
    Modelize a Publication. A Publication can be posted to a Group with the GroupPost model.
    """
    class Meta:
        pass

    # Warning! Both can be NULL !
    poster_user = models.ForeignKey(User, null=True, related_name='created_publications', on_delete=models.SET_NULL)
    poster_group = models.ForeignKey(Group, null=True, related_name='created_publications', on_delete=models.SET_NULL)

    # Link to event ?
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    body = models.TextField()

    # Related fields
    #   - comments (model PublicationComment)
    #   - posts (model GroupPost)
