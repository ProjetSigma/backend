from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_field import GroupField
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_field_value import GroupFieldValue
from sigma_core.serializers.group_field_value import GroupFieldValueSerializer

#
class GroupFieldValueTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        self.group_member_value_url = '/group-field-value/'

        self.nomember = User.objects.create(email='nomember@sigma.fr', lastname='Nomembre', firstname='Bemmonre');
        self.memberA = User.objects.create(email='memberA@sigma.fr', lastname='MembreB', firstname='Bremmeb');
        self.memberB = User.objects.create(email='memberB@sigma.fr', lastname='MembreA', firstname='Remameb');
        self.admin = User.objects.create(email='admin@sigma.fr', lastname='Admin', firstname='Nimad');

        self.group = Group.objects.create(name="Groupe de test", description="")

        self.membershipA = GroupMember.objects.create(user=self.memberA, group=self.group)
        self.membershipB = GroupMember.objects.create(user=self.memberB, group=self.group)
        self.adminship = GroupMember.objects.create(user=self.admin, group=self.group, is_administrator=True)

        # Champs protégés/non protégés pour tester la création
        self.protectedFieldCr = GroupField.objects.create(group=self.group, name="Champ protégé", type=GroupField.TYPE_STRING, protected=True)
        self.notProtectedFieldCr = GroupField.objects.create(group=self.group, name="Champ non protégé", type=GroupField.TYPE_STRING)

        # Champs protégés/non protégés, et leurs valeurs correspondantes, pour tester l'update et la suppression
        self.protectedField = GroupField.objects.create(group=self.group, name="Champ protégé", type=GroupField.TYPE_STRING, protected=True)
        self.notProtectedField = GroupField.objects.create(group=self.group, name="Champ non protégé", type=GroupField.TYPE_STRING)

        self.protectedValueA = GroupFieldValue.objects.create(membership=self.membershipA, field=self.protectedField, value='')
        self.protectedValueB = GroupFieldValue.objects.create(membership=self.membershipB, field=self.protectedField, value='')
        self.protectedValueAdmin = GroupFieldValue.objects.create(membership=self.adminship, field=self.protectedField, value='')

        self.notProtectedValueA = GroupFieldValue.objects.create(membership=self.membershipA, field=self.notProtectedField, value='')
        self.notProtectedValueB = GroupFieldValue.objects.create(membership=self.membershipB, field=self.notProtectedField, value='')
        self.notProtectedValueAdmin = GroupFieldValue.objects.create(membership=self.adminship, field=self.notProtectedField, value='')



    ###############################################################################################
    ##     CREATION TESTS                                                                        ##
    ###############################################################################################

    def try_create(self, u, m, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.post(self.group_member_value_url, {'membership': m.id, 'field': f.id, 'value': ''}, format='json')
        self.assertEqual(r.status_code, s)

    def test_create_memberA_in_membershipA_notprotected(self):
        self.try_create(self.memberA, self.membershipA, self.notProtectedFieldCr, status.HTTP_201_CREATED)
    def test_create_memberA_in_membershipB_notprotected(self):
        self.try_create(self.memberA, self.membershipB, self.notProtectedFieldCr, status.HTTP_403_FORBIDDEN)

    def test_create_admin_in_membershipA_notprotected(self):
        self.try_create(self.admin, self.membershipA, self.notProtectedFieldCr, status.HTTP_201_CREATED)
    def test_create_admin_in_adminship_notprotected(self):
        self.try_create(self.admin, self.adminship, self.notProtectedFieldCr, status.HTTP_201_CREATED)

    def test_create_memberA_in_membershipA_protected(self):
        self.try_create(self.memberA, self.membershipA, self.protectedFieldCr, status.HTTP_403_FORBIDDEN)
    def test_create_memberA_in_membershipB_protected(self):
        self.try_create(self.memberA, self.membershipB, self.protectedFieldCr, status.HTTP_403_FORBIDDEN)

    def test_create_admin_in_membershipA_protected(self):
        self.try_create(self.admin, self.membershipA, self.protectedFieldCr, status.HTTP_201_CREATED)
    def test_create_admin_in_adminship_protected(self):
        self.try_create(self.admin, self.adminship, self.protectedFieldCr, status.HTTP_201_CREATED)

    def test_create_already_existing(self):
        self.try_create(self.admin, self.adminship, self.protectedField, status.HTTP_400_BAD_REQUEST)



    ###############################################################################################
    ##     UPDATE TESTS                                                                          ##
    ###############################################################################################

    def try_update(self, u, v, s):
        uv = GroupFieldValueSerializer(v).data
        uv['value'] = "Test"

        self.client.force_authenticate(user=u)
        r = self.client.put(self.group_member_value_url + str(v.id) + '/', uv, format='json')

        self.assertEqual(r.status_code, s)
        if s == status.HTTP_200_OK:
            self.assertEqual(GroupFieldValueSerializer(GroupFieldValue.objects.all().get(id=v.id)).data, uv)

    def test_update_memberA_in_valueA_notprotected(self):
        self.try_update(self.memberA, self.notProtectedValueA, status.HTTP_200_OK)
    def test_update_memberA_in_valueB_notprotected(self):
        self.try_update(self.memberA, self.notProtectedValueB, status.HTTP_403_FORBIDDEN)

    def test_update_admin_in_valueA_notprotected(self):
        self.try_update(self.admin, self.notProtectedValueA, status.HTTP_200_OK)
    def test_update_admin_in_valueAdmin_notprotected(self):
        self.try_update(self.admin, self.notProtectedValueAdmin, status.HTTP_200_OK)

    def test_update_memberA_in_valueA_protected(self):
        self.try_update(self.memberA, self.protectedValueA, status.HTTP_403_FORBIDDEN)
    def test_update_memberA_in_valueB_protected(self):
        self.try_update(self.memberA, self.protectedValueB, status.HTTP_403_FORBIDDEN)

    def test_update_admin_in_valueA_protected(self):
        self.try_update(self.admin, self.protectedValueA, status.HTTP_200_OK)
    def test_update_admin_in_valueAdmin_protected(self):
        self.try_update(self.admin, self.protectedValueAdmin, status.HTTP_200_OK)




=======
        
        
    

    ###############################################################################################
    ##     DESTROY TESTS                                                                         ##
    ###############################################################################################

    def try_destroy(self, u, v, s):
        self.client.force_authenticate(user=u)
        r = self.client.delete(self.group_member_value_url + str(v.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

    def test_destroy_memberA_in_valueA_notprotected(self):
        self.try_destroy(self.memberA, self.notProtectedValueA, status.HTTP_204_NO_CONTENT)
    def test_destroy_memberA_in_valueB_notprotected(self):
        self.try_destroy(self.memberA, self.notProtectedValueB, status.HTTP_403_FORBIDDEN)

    def test_destroy_admin_in_valueA_notprotected(self):
        self.try_destroy(self.admin, self.notProtectedValueA, status.HTTP_204_NO_CONTENT)
    def test_destroy_admin_in_valueAdmin_notprotected(self):
        self.try_destroy(self.admin, self.notProtectedValueAdmin, status.HTTP_204_NO_CONTENT)

    def test_destroy_memberA_in_valueA_protected(self):
        self.try_destroy(self.memberA, self.protectedValueA, status.HTTP_403_FORBIDDEN)
    def test_destroy_memberA_in_valueB_protected(self):
        self.try_destroy(self.memberA, self.protectedValueB, status.HTTP_403_FORBIDDEN)

    def test_destroy_admin_in_valueA_protected(self):
        self.try_destroy(self.admin, self.protectedValueA, status.HTTP_204_NO_CONTENT)
    def test_destroy_admin_in_valueAdmin_protected(self):
        self.try_destroy(self.admin, self.protectedValueAdmin, status.HTTP_204_NO_CONTENT)


    ###############################################################################################
    ##     LIST TESTS                                                                            ##
    ###############################################################################################

    # def try_delete(self, u, f, s):
        # self.client.force_authenticate(user=u)
        # r = self.client.post(self.group_field_url + str(f.id) + '/destroy', format='json')
        # self.assertEqual(r.status_code, s)

    # def test_delete_nomember_in_secretgr(self):
        # self.try_delete(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    # def test_delete_nomember_in_normalgr(self):
        # self.try_delete(self.nomember, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    # def test_delete_nomember_in_publicgr(self):
        # self.try_delete(self.nomember, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    # def test_delete_member_in_secretgr(self):
        # self.try_delete(self.member, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    # def test_delete_member_in_normalgr(self):
        # self.try_delete(self.member, self.normalGroupField, status.HTTP_403_FORBIDDEN)
    # def test_delete_member_in_publicgr(self):
        # self.try_delete(self.member, self.publicGroupField, status.HTTP_403_FORBIDDEN)

    # def test_delete_admin_in_secretgr(self):
        # self.try_delete(self.admin, self.secretGroupField, status.HTTP_204_NO_CONTENT)
    # def test_delete_admin_in_normalgr(self):
        # self.try_delete(self.admin, self.normalGroupField, status.HTTP_204_NO_CONTENT)
    # def test_delete_admin_in_publicgr(self):
        # self.try_delete(self.admin, self.publicGroupField, status.HTTP_204_NO_CONTENT)



    ###############################################################################################
    ##     RETRIEVE TESTS                                                                        ##
    ###############################################################################################

    # No need for retrieve tests as retrieving a group field value has the same permission as retrieving the equivalent group field.




    ###############################################################################################
    ##     VALIDATION TESTS                                                                      ##
    ###############################################################################################

    def try_validation(self, t, a, v, p):
        self.client.force_authenticate(user=self.admin)
        f = GroupField.objects.create(group=self.group, name="Champ de test", type=t, accept=a)
        r = self.client.post(self.group_member_value_url, {'membership': self.adminship.id, 'field': f.id, 'value': v}, format='json')
        if p:
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        else:
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


    def test_validation_number(self):
        self.try_validation(GroupField.TYPE_NUMBER, '', 0, True)
        self.try_validation(GroupField.TYPE_NUMBER, '_0', 0, True)
        self.try_validation(GroupField.TYPE_NUMBER, '_10', -66, True)
        self.try_validation(GroupField.TYPE_NUMBER, '-10_42', 12, True)
        self.try_validation(GroupField.TYPE_NUMBER, '-10_', 28, True)

        self.try_validation(GroupField.TYPE_NUMBER, '_-4', -1, False)
        self.try_validation(GroupField.TYPE_NUMBER, '2_', 1, False)
        self.try_validation(GroupField.TYPE_NUMBER, '10_42', 102, False)
        self.try_validation(GroupField.TYPE_NUMBER, '-10_-42', 5, False)



    def test_validation_email(self):
        self.try_validation(GroupField.TYPE_EMAIL, '', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.test', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, 'test', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, 'test.test', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.test', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.test toto.toto', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, '@test.test    test', 'test@test.test', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.fr .com .edu .goov .ko.uka .tg', 'test@gmail.helicoptere.tg', True)
        self.try_validation(GroupField.TYPE_EMAIL, '.fr .com .edu .goov .ko.uka .tg', 'test@gmail.fr', True)

        self.try_validation(GroupField.TYPE_EMAIL, '.test.test', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, '.toto.test', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, 'toto.test', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, '@toto.test', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, '.toto', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, '.fr .com .gmail .tg @troll.tg', 'test@test.test', False)
        self.try_validation(GroupField.TYPE_EMAIL, '.fr .com .gmail .tg @troll.tg', 'test@fr', False)
