from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.school import School
from sigma_core.models.group_member import GroupMember


admin.site.unregister(AuthGroup)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(School)
admin.site.register(GroupMember)
