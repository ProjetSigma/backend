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
        model = Publication

    text = factory.LazyAttribute(lambda obj: faker.text())


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
from sigma_publications.serializers import PublicationSerializer


class PublicationTestsSituation(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        # Situation
        # User0
        #   -> Group0 [Group admin]
        #   -> Group1
        #   -> Group2
        #   -> Publication0 ("draft")
        # User1
        #   -> Group1 [Group admin]
        #       -> GroupPost -> Publication1
        #   -> Publication1
        # User2
        #   -> Group2
        self.users = UserFactory.create_batch(3)
        self.groups = GroupFactory.create_batch(3)
        GroupMemberFactory(user=self.users[0], group=self.groups[0], perm_rank=Group.ADMINISTRATOR_RANK)
        GroupMemberFactory(user=self.users[0], group=self.groups[1])
        GroupMemberFactory(user=self.users[0], group=self.groups[2])
        GroupMemberFactory(user=self.users[1], group=self.groups[1], perm_rank=Group.ADMINISTRATOR_RANK)
        GroupMemberFactory(user=self.users[2], group=self.groups[2])

        # Publications
        self.publications = [PublicationFactory(poster_user=self.users[0]),
                PublicationFactory(poster_user=self.users[1])]
        GroupPostFactory(publication=self.publications[1], group=self.groups[1])

        # Routes
        self.publications_route = '/publication/'


class PublicationTests(PublicationTestsSituation):
    # CREATE
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
        qs = Publication.objects.filter(pk=response.data.get('id'))
        self.assertEqual(qs.filter(poster_user=self.users[0]).count(), 1)
        self.assertEqual(qs.filter(poster_user=self.users[1]).count(), 0)

    def test_create_publication_as_group_ok(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[1], self.groups[1]))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_publication_as_user_ok(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.post(self.publications_route, self.gen_new_publication(self.users[0], None))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # UPDATE
    def test_update_not_authed(self):
        data = PublicationSerializer(self.publications[0]).data
        data['text'] = 'Just edit this'
        response = self.client.put("%s%d/" % (self.publications_route, self.publications[0].id), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_owner(self):
        self.client.force_authenticate(user=self.users[1])
        data = PublicationSerializer(self.publications[0]).data
        data['text'] = 'Just edit this'
        response = self.client.put("%s%d/" % (self.publications_route, self.publications[0].id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_poster_group_read_only(self):
        self.client.force_authenticate(user=self.users[0])
        data = PublicationSerializer(self.publications[0]).data
        data['poster_group'] = self.groups[0].id
        response = self.client.put("%s%d/" % (self.publications_route, self.publications[0].id), data)
        # Response code is 200 ...
        self.publications[0].refresh_from_db()
        self.assertEqual(self.publications[0].poster_group, None)

    def test_update_ok(self):
        self.client.force_authenticate(user=self.users[0])
        data = PublicationSerializer(self.publications[0]).data
        data['text'] = 'Just edit this'
        response = self.client.put("%s%d/" % (self.publications_route, self.publications[0].id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # DESTROY
    def test_delete_not_draft(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.delete("%s%d/" % (self.publications_route, self.publications[1].id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_not_own_publication(self):
        self.client.force_authenticate(user=self.users[1])
        response = self.client.delete("%s%d/" % (self.publications_route, self.publications[0].id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_draft_ok(self):
        self.client.force_authenticate(user=self.users[0])
        response = self.client.delete("%s%d/" % (self.publications_route, self.publications[0].id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
