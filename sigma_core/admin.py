from django.contrib import admin
from django.contrib.auth.models import Group as AuthGroup

from sigma_core.models.user import User
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

#admin.site.register(GroupMember)
#admin.site.register(GroupInvitation)
#admin.site.register(GroupAcknowledgment)
#admin.site.register(SharedPublication)
#admin.site.register(Participation)

admin.site.register(GroupField)
admin.site.register(GroupFieldValue)


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 0

class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_start', 'date_end', 'place_name']
    list_filter = ['date_start', 'date_end']
    search_fields = ['name', 'place_name']
    inlines = [ParticipationInline]

admin.site.register(Event, EventAdmin)

class SharedInline(admin.TabularInline):
    model = SharedPublication
    extra = 0

class PublicationAdmin(admin.ModelAdmin):
    inlines = [SharedInline]
    list_display = ['name', 'group', 'author', 'related_event', 'internal', 'approved']
    list_filter = ['group', 'author', 'internal', 'approved']

admin.site.register(Publication, PublicationAdmin)

class GroupsInline(admin.TabularInline):
    model = GroupMember
    extra = 0

class InvitationsInline(admin.TabularInline):
    model = GroupInvitation
    extra = 0

class UserAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'email', 'is_active', 'is_superuser', 'is_staff']
    list_filter = ['is_active', 'is_superuser', 'is_staff']
    search_fields = ['firstname', 'lastname', 'email']
    inlines = [GroupsInline, InvitationsInline]

admin.site.register(User, UserAdmin)

class MembersInline(admin.TabularInline):
    model = GroupMember
    extra = 0

class ParentsInline(admin.TabularInline):
    model = GroupAcknowledgment
    extra = 0
    fk_name = "subgroup"

class ChildrenInline(admin.TabularInline):
    model = GroupAcknowledgment
    extra = 0
    fk_name = "parent_group"

class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_protected', 'can_anyone_ask', 'need_validation_to_join', 'user_confidentiality']
    list_filter = ['is_protected', 'can_anyone_ask', 'need_validation_to_join']
    search_fields = ['name', 'description']
    inlines = [MembersInline, InvitationsInline, ParentsInline, ChildrenInline]

admin.site.register(Group, GroupAdmin)

