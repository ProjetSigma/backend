from django.db import models
from django.db.models import Q

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from dry_rest_permissions.generics import allow_staff_or_superuser


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related('clusters__group_ptr')

    def create_user(self, email, lastname, firstname, password=None):
        """
        Creates and saves a User with the given email, lastname, firstname and password
        TODO - Generate a unique username.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # username = email # TODO - Generate unique username

        user = self.model(
            email=self.normalize_email(email),
            lastname=lastname,
            firstname=firstname
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, lastname, firstname, password):
        """
        Creates and saves a superuser with the given email, lastname, firstname and password.
        """
        user = self.create_user(email, lastname, firstname, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser):
    """
    User are identified by their email. Lastname and firstname are required.
    """
    email = models.EmailField(max_length=254, unique=True)
    lastname = models.CharField(max_length=255)
    firstname = models.CharField(max_length=128)
    # username = models.CharField(max_length=128, unique=True) # TODO - Add unique username for frontend URLs
    phone = models.CharField(max_length=20, blank=True)
    photo = models.OneToOneField('sigma_files.Image', blank=True, null=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    join_date = models.DateTimeField(auto_now_add=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    clusters = models.ManyToManyField('Cluster', related_name="cluster_users") # users should be members of at least one cluster

    objects = UserManager()

    invited_to_groups = models.ManyToManyField('Group', blank=True, related_name="invited_users");
    groups = models.ManyToManyField('Group', through='GroupMember', related_name='users')

    # Related fields:
    #   - memberships (model GroupMember)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['lastname', 'firstname']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return "{} {}".format(self.lastname, self.firstname)

    def get_short_name(self):
        return self.email

    def is_sigma_admin(self):
        return self.is_staff or self.is_superuser

    def is_in_cluster(self, cluster):
        return cluster in self.clusters.all()

    def has_common_cluster(self, user):
        """
        Return True iff self has a cluster in common with user.
        """
        return len(set(self.clusters.all().values_list('id', flat=True)).intersection(user.clusters.all().values_list('id', flat=True))) > 0

    def has_common_group(self, user):
        """
        Return True iff self has a group in common with user.
        """
        return len(set(self.memberships.all().values_list('group', flat=True)).intersection(user.memberships.all().values_list('group', flat=True))) > 0

    def get_group_membership(self, group):
        from sigma_core.models.group_member import GroupMember
        from sigma_core.models.group import Group
        try:
            return self.memberships.get(group=group)
        except GroupMember.DoesNotExist:
            return None

    def is_group_member(self, g):
        from sigma_core.models.group_member import GroupMember
        mem = self.get_group_membership(g)
        return mem is not None and mem.is_accepted()

    def can_invite(self, group):
        from sigma_core.models.group_member import GroupMember
        mem = self.get_group_membership(group)
        return mem is not None and mem.perm_rank >= group.req_rank_invite

    def can_accept_join_requests(self, group):
        from sigma_core.models.group_member import GroupMember
        if self.is_sigma_admin():
            return True
        mem = self.get_group_membership(group)
        return mem is not None and mem.perm_rank >= group.req_rank_accept_join_requests

    def can_modify_group_infos(self, group):
        from sigma_core.models.group_member import GroupMember
        mem = self.get_group_membership(group)
        return mem is not None and mem.perm_rank >= group.req_rank_modify_group_infos

    def has_group_admin_perm(self, group):
        from sigma_core.models.group_member import GroupMember
        from sigma_core.models.group import Group
        if self.is_sigma_admin():
            return True
        mem = self.get_group_membership(group)
        return mem is not None and mem.perm_rank == Group.ADMINISTRATOR_RANK

    def is_invited_to_group_id(self, groupId):
        return self.invited_to_groups.filter(pk=groupId).exists()

    def get_groups_with_confirmed_membership(self):
        from sigma_core.models.group_member import GroupMember
        return GroupMember.objects.filter(Q(user=self) & Q(perm_rank__gte=1)).values_list('group', flat=True)

    ###############
    # Permissions #
    ###############

    # Perms for admin site
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
