import factory

from django.utils.text import slugify

from sigma_core.models.user import User
from sigma_core.models.group import Group

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    lastname = factory.Faker('last_name')
    firstname = factory.Faker('first_name')
    email = factory.LazyAttribute(lambda obj: '%s.%s@school.edu' % (slugify(obj.firstname), slugify(obj.lastname)))


class AdminUserFactory(UserFactory):
    is_staff = True


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: 'Group %d' % n)
    
