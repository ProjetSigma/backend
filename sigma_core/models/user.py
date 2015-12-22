from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
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

    is_active = models.BooleanField(default=True)
    last_modified = models.DateTimeField(auto_now=True)
    join_date = models.DateTimeField(auto_now_add=True)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['lastname', 'firstname']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return "{} {}".format(self.lastname, self.firstname)

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        TODO - Implement permissions
        """
        return True

    def has_module_perms(self, app_label):
        """
        TODO - Implement permissions
        """
        return True
