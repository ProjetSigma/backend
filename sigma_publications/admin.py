from django.contrib import admin

from sigma_publications.models import Publication, GroupPost, PublicationComment


admin.site.register(Publication)
admin.site.register(GroupPost)
admin.site.register(PublicationComment)
