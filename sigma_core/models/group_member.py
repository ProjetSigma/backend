from django.db import models
from django.http import Http404

from dry_rest_permissions.generics import allow_staff_or_superuser

from sigma_core.models.user import User
from sigma_core.models.group import Group


class GroupMember(models.Model):
    """
    Modelize a membership relation between an User and a Group.
    """
    class Meta:
        # TODO: Make a primary key once Django supports it
        unique_together = (("user", "group"),)

    user = models.ForeignKey(User, related_name='memberships')
    group = models.ForeignKey(Group, related_name='memberships')
    created = models.DateTimeField(auto_now_add=True)
    join_date = models.DateField(blank=True, null=True)
    leave_date = models.DateField(blank=True, null=True)
    perm_rank = models.SmallIntegerField(blank=False, default=1)


    def can_invite(self):
        return self.perm_rank >= self.group.req_rank_invite

    def can_kick(self):
        return self.perm_rank >= self.group.req_rank_kick

    def is_accepted(self):
        return self.perm_rank > 0

    def __str__(self):
        return "User \"%s\" r%d in Group \"%s\"" % (self.user.__str__(), self.perm_rank, self.group.__str__())

    # Perms for admin site
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Permissions
    @staticmethod
    def has_read_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        try:
            # Not optimal. IDEA: pass group and user object through request? 
            group = Group.objects.get(pk=request.data.get('group', None))
            user = User.objects.get(pk=request.data.get('user', None))
        except (Group.DoesNotExist, User.DoesNotExist):
            raise Http404()

        if request.user == user:
            return group.can_anyone_join()
        if group.can_anyone_join():
            # To prevent abusive addition of people to an open group
            return False
        return request.user.can_invite(group)

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        """
        TODO: implement that.
        """
        return True
