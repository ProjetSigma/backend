import factory
from faker import Factory as FakerFactory

from django.utils.text import slugify

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.cluster import Cluster
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_member_value import GroupMemberValue
from sigma_core.models.group_field import GroupField

from sigma_publications.models import Publication, GroupPost, PublicationComment

################################
##     FACTORIES              ##
################################

faker = FakerFactory.create('fr_FR')
class PublicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    title = factory.LazyAttribute(lambda obj: faker.last_name())
    body = factory.LazyAttribute(lambda obj: faker.text())


class GroupPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupPost


class PublicationCommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PublicationComment

    comment = factory.LazyAttribute(lambda obj: faker.text())


################################
##   PUBLICATION TESTS        ##
################################

from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.tests.factories import UserFactory, GroupFactory, AdminUserFactory, GroupMemberFactory


class PublicationTestsSituation(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        # Situation
        # User0
        #   -> Group0
        #   -> Group1
        #   -> Group2
        # User1
        #   -> Group1 [Group admin]
        # User2
        #   -> Group2
        self.users = UserFactory.create_batch(3)
        self.groups = GroupFactory.create_batch(3)
        GroupMemberFactory(user=self.users[0], group=self.groups[0])
        GroupMemberFactory(user=self.users[0], group=self.groups[1])
        GroupMemberFactory(user=self.users[0], group=self.groups[2])
        GroupMemberFactory(user=self.users[1], group=self.groups[1], perm_rank=Group.ADMINISTRATOR_RANK)
        GroupMemberFactory(user=self.users[2], group=self.groups[2])

        # Routes
        self.publications_route = '/publication/'


class PublicationTests(PublicationTestsSituation):
    def gen_new_publication(self, poster_user, poster_group):
        pub = {'text' : 'Random text', 'poster_user': '', 'poster_group' : ''}
        if poster_user is not None:
            pub['poster_user'] = poster_user.id
        if poster_group is not None:
            pub['poster_group'] = poster_group.id
        return pub

    def test_create_publication_not_authed(self):
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[0], None))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_publication_as_group_not_group_member(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[1], self.groups[0]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_publication_as_group_no_permission(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[0], self.groups[1]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_publication_as_someone_else(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[1], None))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Publication.objects.filter(poster_user=self.users[0]).count(), 1)
        self.assertEqual(Publication.objects.filter(poster_user=self.users[1]).count(), 0)

    def test_create_publication_as_group_ok(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[1], self.groups[1]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_publication_as_user_ok(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[0], None))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
