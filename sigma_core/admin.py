from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
from sigma_core.models.group import Group, GroupAcknowledgment
from sigma_core.models.cluster import Cluster
from sigma_core.models.group_member import GroupMember


admin.site.unregister(AuthGroup)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Cluster)
admin.site.register(GroupAcknowledgment)
admin.site.register(GroupMember)
