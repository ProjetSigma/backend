from django.db import models

from sigma_core.models.user import User

class PublicationComment(models.Model):
    """
    Modelize a comment on a Publication
    """
    class Meta:
        pass

    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    publication = models.ForeignKey('Publication', related_name='comments', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comment = models.TextField()
