from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from dry_rest_permissions.generics import allow_staff_or_superuser


class UserManager(BaseUserManager):
    # TODO: Determine whether 'memberships' fields needs to be retrieved every time or not...
    # def get_queryset(self):
    #     return super(UserManager, self).get_queryset().prefetch_related('memberships', 'invited_to_groups')

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
    photo = models.OneToOneField('sigma_files.Image', null=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    join_date = models.DateTimeField(auto_now_add=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    invited_to_groups = models.ManyToManyField('Group', blank=True, related_name="invited_users");

    # Related fields:
    #   - memberships (model UserGroup)

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

    ###############
    # Permissions #
    ###############

    # Perms for admin site
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    # End of admin site permissions

    @staticmethod
    def has_read_permission(request):
        """
        Only authenticated users can retrieve an users list.
        """
        return True

    def has_object_read_permission(self, request):
        """
        Only authenticated users can retrieve an user.
        """
        return True

    @staticmethod
    def has_write_permission(request):
        """
        Everybody can edit or create users, but with certain restraints specified in below functions.
        By the way, everybody can change one's password or reset it.
        """
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        """
        Only Sigma admins can create users.
        """
        return False

    def has_object_write_permission(self, request):
        """
        Nobody has all write permissions on an user (especially, nobody can delete an user).
        """
        return False

    @allow_staff_or_superuser
    def has_object_update_permission(self, request):
        """
        Only Sigma admin and oneself can edit an user.
        """
        return request.user.id == self.id
