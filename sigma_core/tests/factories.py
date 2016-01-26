import factory
from faker import Factory as FakerFactory

from django.utils.text import slugify

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field import GroupField

faker = FakerFactory.create('fr_FR')

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    lastname = factory.LazyAttribute(lambda obj: faker.last_name())
    firstname = factory.LazyAttribute(lambda obj: faker.first_name())
    email = factory.LazyAttribute(lambda obj: '%s.%s@school.edu' % (slugify(obj.firstname), slugify(obj.lastname)))
    phone = factory.LazyAttribute(lambda obj: faker.phone_number())


class AdminUserFactory(UserFactory):
    is_staff = True


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: 'Group %d' % n)


class GroupFieldFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupField

    name = factory.Sequence(lambda n: 'Field %d' % n)


class GroupMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupMember

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    join_date = factory.LazyAttribute(lambda obj: faker.date())
