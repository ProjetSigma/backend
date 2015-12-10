from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.user_group import UserGroup


admin.site.unregister(AuthGroup)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(UserGroup)
