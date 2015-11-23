from django.contrib import admin
from django.contrib.auth.models import Group

from sigma_core.models.user import User

admin.site.unregister(Group)
admin.site.register(User)
