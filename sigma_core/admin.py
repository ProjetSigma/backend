from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
from sigma_core.models.cluster import Cluster
from sigma_core.models.group import Group
from sigma_core.models.group_acknowledgment import GroupAcknowledgment
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field import GroupField
from sigma_core.models.group_field_value import GroupFieldValue
from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.models.participation import Participation
from sigma_core.models.publication import Publication
from sigma_core.models.event import Event
from sigma_core.models.shared_publication import SharedPublication


admin.site.unregister(AuthGroup)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Cluster)
admin.site.register(GroupAcknowledgment)
admin.site.register(GroupMember)
admin.site.register(GroupField)
admin.site.register(GroupFieldValue)
admin.site.register(GroupInvitation)
admin.site.register(Participation)
admin.site.register(Publication)
admin.site.register(Event)
admin.site.register(SharedPublication)
