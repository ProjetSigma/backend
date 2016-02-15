from django.db import models

from sigma_core.models.user import User
from sigma_core.models.group import Group

class Publication(models.Model):
    """
    Modelize a Publication. A Publication can be posted to a Group with the GroupPost model.
    """

    # Warning! Both can be NULL !
    poster_user = models.ForeignKey(User, null=True, related_name='created_publications', on_delete=models.SET_NULL)
    poster_group = models.ForeignKey(Group, blank=True, null=True, related_name='created_publications', on_delete=models.SET_NULL)

    # Link to event ?
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    text = models.TextField()

    posted_in = models.ManyToManyField(Group, through='GroupPost', related_name="publications")

    # Related fields
    #   - comments (model PublicationComment)
    #   - posts (model GroupPost)
    #   - posted_in (model Group.publications through GroupPost)


class GroupPost(models.Model):
    """
    Modelize a Post on a Group. A Post is a link between a Publication and a Group.
    """

    # Poster ?
    group = models.ForeignKey(Group, related_name='posts', on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, related_name='posts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class PublicationComment(models.Model):
    """
    Modelize a comment on a Publication
    """

    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    publication = models.ForeignKey('Publication', related_name='comments', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    comment = models.TextField()
