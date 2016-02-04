from django.db import models


class PublicationComment(models.Model):
    """
    Modelize a comment on a Publication
    """
    class Meta:
        pass

    user = models.ForeignKey('User', related_name='comments', on_delete=models.DELETE)
    publication = models.ForeignKey('Publication', related_name='comments', on_delete=models.DELETE)

    created = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
