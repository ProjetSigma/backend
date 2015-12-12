from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
from sigma_core.models.group import Group


admin.site.unregister(AuthGroup)
admin.site.register(User)
admin.site.register(Group)
