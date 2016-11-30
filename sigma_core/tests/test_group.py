from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field import GroupField
from sigma_core.serializers.group_field import GroupFieldSerializer


class GroupTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        self.group_url = '/group/'

        self.nomember = User.objects.create(email='nomember@sigma.fr', lastname='Nomembre', firstname='Bemmonre');
        self.member = User.objects.create(email='member@sigma.fr', lastname='Membre', firstname='Remmeb');
        self.admin = User.objects.create(email='admin@sigma.fr', lastname='Admin', firstname='Nimad');

        self.secretGroup = Group.objects.create(name="Groupe Secret", description="", visibility=Group.CONF_SECRET)
        self.normalGroup = Group.objects.create(name="Groupe Normal", description="", visibility=Group.CONF_NORMAL)
        self.publicGroup = Group.objects.create(name="Groupe Public", description="", visibility=Group.CONF_PUBLIC)

        GroupMember.objects.create(user=self.member, group=self.secretGroup)
        GroupMember.objects.create(user=self.member, group=self.normalGroup)
        GroupMember.objects.create(user=self.member, group=self.publicGroup)

        GroupMember.objects.create(user=self.admin, group=self.secretGroup, is_super_administrator=True)
        GroupMember.objects.create(user=self.admin, group=self.normalGroup, is_super_administrator=True)
        GroupMember.objects.create(user=self.admin, group=self.publicGroup, is_super_administrator=True)

        self.secretGroupField = GroupField.objects.create(group=self.secretGroup, name="Champ dans groupe secret", type=GroupField.TYPE_STRING)
        self.normalGroupField = GroupField.objects.create(group=self.normalGroup, name="Champ dans groupe normal", type=GroupField.TYPE_STRING)
        self.publicGroupField = GroupField.objects.create(group=self.publicGroup, name="Champ dans groupe public", type=GroupField.TYPE_STRING)


    ###############################################################################################
    ##     CREATION TESTS                                                                        ##
    ###############################################################################################

    def try_create(self, u, g, s):
        self.client.force_authenticate(user=u)
        r = self.client.post(self.group_field_url, {'group': g.id, 'name': 'Test', 'type': GroupField.TYPE_STRING, 'accept':''}, format='json')
        self.assertEqual(r.status_code, s)

    def test_create_nomember_in_secretgr(self):
        self.try_create(self.nomember, self.secretGroup, status.HTTP_403_FORBIDDEN)
    def test_create_nomember_in_normalgr(self):
        self.try_create(self.nomember, self.normalGroup, status.HTTP_403_FORBIDDEN)
    def test_create_nomember_in_publicgr(self):
        self.try_create(self.nomember, self.publicGroup, status.HTTP_403_FORBIDDEN)

    def test_create_member_in_secretgr(self):
        self.try_create(self.member, self.secretGroup, status.HTTP_403_FORBIDDEN)
    def test_create_member_in_normalgr(self):
        self.try_create(self.member, self.normalGroup, status.HTTP_403_FORBIDDEN)
    def test_create_member_in_publicgr(self):
        self.try_create(self.member, self.publicGroup, status.HTTP_403_FORBIDDEN)

    def test_create_admin_in_secretgr(self):
        self.try_create(self.admin, self.secretGroup, status.HTTP_201_CREATED)
    def test_create_admin_in_normalgr(self):
        self.try_create(self.admin, self.normalGroup, status.HTTP_201_CREATED)
    def test_create_admin_in_publicgr(self):
        self.try_create(self.admin, self.publicGroup, status.HTTP_201_CREATED)

    ###############################################################################################
    ##     UPDATE TESTS                                                                          ##
    ###############################################################################################

    def try_update(self, u, f, s):
        uf = GroupFieldSerializer(f).data
        uf['name'] = "Autre nom"

        self.client.force_authenticate(user=u)
        r = self.client.put(self.group_field_url + str(f.id) + '/', uf, format='json')

        self.assertEqual(r.status_code, s)
        if s == status.HTTP_200_OK:
            self.assertEqual(GroupFieldSerializer(GroupField.objects.all().get(id=f.id)).data, uf)

    def test_update_nomember_in_secretgr(self):
        self.try_update(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_update_nomember_in_normalgr(self):
        self.try_update(self.nomember, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_update_nomember_in_publicgr(self):
        self.try_update(self.nomember, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_update_member_in_secretgr(self):
        self.try_update(self.member, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_update_member_in_normalgr(self):
        self.try_update(self.member, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_update_member_in_publicgr(self):
        self.try_update(self.member, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_update_admin_in_secretgr(self):
        self.try_update(self.admin, self.secretGroupField, status.HTTP_200_OK)
    def test_update_admin_in_normalgr(self):
        self.try_update(self.admin, self.normalGroupField, status.HTTP_200_OK)
    def test_update_admin_in_publicgr(self):
        self.try_update(self.admin, self.publicGroupField, status.HTTP_200_OK)

    ###############################################################################################
    ##     DESTROY TESTS                                                                         ##
    ###############################################################################################

    def try_destroy(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.delete(self.group_field_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

    def test_destroy_nomember_in_secretgr(self):
        self.try_destroy(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_in_normalgr(self):
        self.try_destroy(self.nomember, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_in_publicgr(self):
        self.try_destroy(self.nomember, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_destroy_member_in_secretgr(self):
        self.try_destroy(self.member, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_in_normalgr(self):
        self.try_destroy(self.member, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_in_publicgr(self):
        self.try_destroy(self.member, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_destroy_admin_in_secretgr(self):
        self.try_destroy(self.admin, self.secretGroupField, status.HTTP_204_NO_CONTENT)
    def test_destroy_admin_in_normalgr(self):
        self.try_destroy(self.admin, self.normalGroupField, status.HTTP_204_NO_CONTENT)
    def test_destroy_admin_in_publicgr(self):
        self.try_destroy(self.admin, self.publicGroupField, status.HTTP_204_NO_CONTENT)


    ###############################################################################################
    ##     LIST TESTS                                                                            ##
    ###############################################################################################

    def try_delete(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.post(self.group_field_url + str(f.id) + '/destroy', format='json')
        self.assertEqual(r.status_code, s)

    def test_delete_nomember_in_secretgr(self):
        self.try_delete(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_delete_nomember_in_normalgr(self):
        self.try_delete(self.nomember, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_delete_nomember_in_publicgr(self):
        self.try_delete(self.nomember, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_delete_member_in_secretgr(self):
        self.try_delete(self.member, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    def test_delete_member_in_normalgr(self):
        self.try_delete(self.member, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    def test_delete_member_in_publicgr(self):
        self.try_delete(self.member, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    def test_delete_admin_in_secretgr(self):
        self.try_delete(self.admin, self.secretGroupField, status.HTTP_204_NO_CONTENT)
    def test_delete_admin_in_normalgr(self):
        self.try_delete(self.admin, self.normalGroupField, status.HTTP_204_NO_CONTENT)
    def test_delete_admin_in_publicgr(self):
        self.try_delete(self.admin, self.publicGroupField, status.HTTP_204_NO_CONTENT)



    ###############################################################################################
    ##     RETRIEVE TESTS                                                                        ##
    ###############################################################################################

    def try_retrieve(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.get(self.group_field_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

        if r.status_code == status.HTTP_200_OK:
            self.assertEqual( r.data, GroupFieldSerializer(f).data )


    def test_retrieve_nomember_in_secretgr(self):
        self.try_retrieve(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)

    #TODO : CHANGE IT WHEN THE ADEQUATE FUNCTIONS WILL BE CREATED
    def test_retrieve_nomember_in_normalgr(self):
        self.try_retrieve(self.nomember, self.normalGroupField, status.HTTP_200_FORBIDDEN)
    def test_retrieve_nomember_in_publicgr(self):
        self.try_retrieve(self.nomember, self.publicGroupField, status.HTTP_200_OK)

    def test_retrieve_member_in_secretgr(self):
        self.try_retrieve(self.member, self.secretGroupField, status.HTTP_200_OK)
    def test_retrieve_member_in_normalgr(self):
        self.try_retrieve(self.member, self.normalGroupField, status.HTTP_200_OK)
    def test_retrieve_member_in_publicgr(self):
        self.try_retrieve(self.member, self.publicGroupField, status.HTTP_200_OK)

    def test_retrieve_admin_in_secretgr(self):
        self.try_retrieve(self.admin, self.secretGroupField, status.HTTP_200_OK)
    def test_retrieve_admin_in_normalgr(self):
        self.try_retrieve(self.admin, self.normalGroupField, status.HTTP_200_OK)
    def test_retrieve_admin_in_publicgr(self):
        self.try_retrieve(self.admin, self.publicGroupField, status.HTTP_200_OK)



    ###############################################################################################
    ##     VALIDATION TESTS                                                                      ##
    ###############################################################################################

    def try_validation(self, t, v, p):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(self.group_field_url, {'group': self.secretGroup.id, 'name': 'Test', 'type': t, 'accept': v}, format='json')
        if p:
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


    def test_validation_number(self):
        self.try_validation(GroupField.TYPE_NUMBER, '', True)
        self.try_validation(GroupField.TYPE_NUMBER, '_', True)
        self.try_validation(GroupField.TYPE_NUMBER, '12_', True)
        self.try_validation(GroupField.TYPE_NUMBER, '_43', True)
        self.try_validation(GroupField.TYPE_NUMBER, '12_-43', True)
        self.try_validation(GroupField.TYPE_NUMBER, '12_42', True)
        self.try_validation(GroupField.TYPE_NUMBER, '-43_12', True)

        self.try_validation(GroupField.TYPE_NUMBER, '43_12-10', False)
        self.try_validation(GroupField.TYPE_NUMBER, '43__12', False)
        self.try_validation(GroupField.TYPE_NUMBER, '4.3_', False)
        self.try_validation(GroupField.TYPE_NUMBER, '12', False)
        self.try_validation(GroupField.TYPE_NUMBER, '_10_', False)


    def test_validation_email(self):
        self.try_validation(GroupField.TYPE_EMAIL, '', True)
        self.try_validation(GroupField.TYPE_EMAIL, 'toto', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.toto', True)
        self.try_validation(GroupField.TYPE_EMAIL, 'test.toto', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.test.toto', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.toto', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.toto .test.tata', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.toto      .test.tata', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.test.toto      @test.tata .toto .tata @tata.toto .toto.tata', True)

        self.try_validation(GroupField.TYPE_EMAIL, 'test.', False)
        self.try_validation(GroupField.TYPE_EMAIL, 'maieuh@', False)
        self.try_validation(GroupField.TYPE_EMAIL, 'maieuh@test.toto', False)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.toto, test.tata', False)
