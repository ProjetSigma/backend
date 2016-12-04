import json

from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.renderers import JSONRenderer

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.serializers.user import UserSerializer


class GroupMemberTest(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.group_member_url = "/group-member/"


        self.nomember = User.objects.create(email='nomember@sigma.fr', lastname='Nomembre', firstname='Bemmonre');
        self.member = User.objects.create(email='member@sigma.fr', lastname='Membre', firstname='Remmeb');
        #admin and superadmin in the group, not in the whole website
        self.admin = User.objects.create(email='member_admin@sigma.fr', lastname='Membreadmin', firstname='Felix');
        self.superadmin = User.objects.create(email='member_superadmin@sigma.fr', lastname='Membre_superadmin', firstname='Alex');

        #member2 and admin2 to differenciate the case when you want to modify yourself
        #and when you want to modify someone who isn't you but has the same rank
        #only one superadmin so no need to create self.superadmin2
        self.member2=User.objects.create(email='member@sigma.fr', lastname='Membre22');
        self.admin2 = User.objects.create(email='member_admin@sigma.fr', lastname='Membreadmin2', firstname='Felix2');

        #TODO : implement retrieve according to the visibility of the group
        self.group = Group.objects.create(name="Groupe", description="")

        self.mb_member = GroupMember.objects.create(user=self.member, group=self.group)
        self.mb_admin = GroupMember.objects.create(user=self.admin, group=self.group, is_administrator=True)
        self.mb_superadmin = GroupMember.objects.create(user=self.superadmin, group=self.group, is_super_administrator=True)

        self.mb_member2 = GroupMember.objects.create(user=self.member2, group=self.group)
        self.mb_admin2 = GroupMember.objects.create(user=self.admin2, group=self.group, is_administrator=True)


    ###############################################################################################
    ##     UPDATE TESTS                                                                          ##
    ###############################################################################################

    def modifiedJson(m_ship,right_to_change_str):
        serializer = GroupMemberSerializer(m_ship)
        serializer[right_to_change_str] = not serializer[right_to_change_str]
        return JSONRenderer().render(serializer.data)



    # u = the user who tries to modify the data
    # f = membership which is going to be modified
    # s = status_code that should be sent
    # uf = json of the modified m_ship
    def try_update(self, u, f, s):

        self.client.force_authenticate(user=u)
        r = self.client.put(self.group_member_url + str(f.id) + '/', uf, format='json')

        self.assertEqual(r.status_code, s)

    def test_update_nomember_to_member_basic_rights(self):
        self.try_update(self.nomember, self.mb_normal, modifiedJson(self.mb_normal,'can_invite'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_admin_basic_rights(self):
        self.try_update(self.nomember, self.mb_admin, modifiedJson(self.mb_admin,'can_invite'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_superadmin_basic_rights(self):
        self.try_update(self.nomember, self.mb_superadmin, modifiedJson(self.mb_superadmin,'can_invite'), status.HTTP_403_FORBIDDEN)

    def test_update_member_to_member2_basic_rights(self):
        self.try_update(self.member, self.mb_member2, modifiedJson(self.mb_member2,'can_invite'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_admin_basic_rights(self):
        self.try_update(self.member, self.mb_admin, modifiedJson(self.mb_admin,'can_invite'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_superadmin_basic_rights(self):
        self.try_update(self.member, self.mb_superadmin, modifiedJson(self.mb_superadmin,'can_invite'), status.HTTP_403_FORBIDDEN)

    def test_update_admin_to_member_basic_rights(self):
        self.try_update(self.admin, self.mb_member, modifiedJson(self.mb_member,'can_invite'), status.HTTP_200_OK)
    def test_update_admin_to_admin_basic_rights(self):
        self.try_update(self.admin, self.mb_admin, modifiedJson(self.mb_admin,'can_invite'), status.HTTP_200_OK)
    def test_update_admin_to_admin2_basic_rights(self):
        self.try_update(self.admin, self.mb_admin2, modifiedJson(self.mb_admin2,'can_invite'), status.HTTP_403_FORBIDDEN)
    def test_update_admin_to_superadmin_basic_rights(self):
        self.try_update(self.admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'can_invite'), status.HTTP_403_FORBIDDEN)

    def test_update_super_admin_to_member_basic_rights(self):
        self.try_update(self.super_admin, self.mb_member, modifiedJson(self.mb_member,'can_invite'), status.HTTP_200_OK)
    def test_update_super_admin_to_admin_basic_rights(self):
        self.try_update(self.super_admin, self.mb_admin, modifiedJson(self.mb_admin,'can_invite'), status.HTTP_200_OK)
    def test_update_superadmin_to_superadmin_basic_rights(self):
        self.try_update(self.super_admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'can_invite'), status.HTTP_403_FORBIDDEN)


    def test_update_nomember_to_member_is_admin(self):
        self.try_update(self.nomember, self.mb_normal, modifiedJson(self.mb_normal,'is_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_admin_is_admin(self):
        self.try_update(self.nomember, self.mb_admin, modifiedJson(self.mb_admin,'is_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_superadmin_is_admin(self):
        self.try_update(self.nomember, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_member_to_member2_is_admin(self):
        self.try_update(self.member, self.mb_member2, modifiedJson(self.mb_member2,'is_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_admin_is_admin(self):
        self.try_update(self.member, self.mb_admin, modifiedJson(self.mb_admin,'is_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_superadmin_is_admin(self):
        self.try_update(self.member, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_admin_to_member_is_admin(self):
        self.try_update(self.admin, self.mb_member, modifiedJson(self.mb_member,'is_administrator'), status.HTTP_200_OK)
    def test_update_admin_to_admin_is_admin(self):
        self.try_update(self.admin, self.mb_admin, modifiedJson(self.mb_admin,'is_administrator'), status.HTTP_200_OK)
    def test_update_admin_to_admin2_is_admin(self):
        self.try_update(self.admin, self.mb_admin2, modifiedJson(self.mb_admin2,'is_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_admin_to_superadmin_is_admin(self):
        self.try_update(self.admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_super_admin_to_member_is_admin(self):
        self.try_update(self.super_admin, self.mb_member, modifiedJson(self.mb_member,'is_administrator'), status.HTTP_200_OK)
    def test_update_super_admin_to_admin_is_admin(self):
        self.try_update(self.super_admin, self.mb_admin, modifiedJson(self.mb_admin,'is_administrator'), status.HTTP_200_OK)
    def test_update_superadmin_to_superadmin_is_admin(self):
        self.try_update(self.super_admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_administrator'), status.HTTP_403_FORBIDDEN)



    def test_update_nomember_to_member_is_superadmin(self):
        self.try_update(self.nomember, self.mb_normal, modifiedJson(self.mb_normal,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_admin_is_superadmin(self):
        self.try_update(self.nomember, self.mb_admin, modifiedJson(self.mb_admin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_nomember_to_superadmin_is_superadmin(self):
        self.try_update(self.nomember, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_member_to_member2_is_superadmin(self):
        self.try_update(self.member, self.mb_member2, modifiedJson(self.mb_member2,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_admin_is_superadmin(self):
        self.try_update(self.member, self.mb_admin, modifiedJson(self.mb_admin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_member_to_superadmin_is_superadmin(self):
        self.try_update(self.member, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_admin_to_member_is_superadmin(self):
        self.try_update(self.admin, self.mb_member, modifiedJson(self.mb_member,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_admin_to_admin_is_superadmin(self):
        self.try_update(self.admin, self.mb_admin, modifiedJson(self.mb_admin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_admin_to_admin2_is_superadmin(self):
        self.try_update(self.admin, self.mb_admin2, modifiedJson(self.mb_admin2,'is_super_administrator'), status.HTTP_403_FORBIDDEN)
    def test_update_admin_to_superadmin_is_superadmin(self):
        self.try_update(self.admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)

    def test_update_super_admin_to_member_is_superadmin(self):
        self.try_update(self.super_admin, self.mb_member, modifiedJson(self.mb_member,'is_super_administrator'), status.HTTP_200_OK)
    def test_update_super_admin_to_admin_is_superadmin(self):
        self.try_update(self.super_admin, self.mb_admin, modifiedJson(self.mb_admin,'is_super_administrator'), status.HTTP_200_OK)
    def test_update_superadmin_to_superadmin_is_superadmin(self):
        self.try_update(self.super_admin, self.mb_superadmin, modifiedJson(self.mb_superadmin,'is_super_administrator'), status.HTTP_403_FORBIDDEN)

    ###############################################################################################
    ##     destroy TESTS                                                                         ##
    ###############################################################################################

    def try_destroy(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.delete(self.group_member_url + str(self.f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

    def test_destroy_nomember_to_member(self):
        self.try_destroy(self.nomember, self.mb_member, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_to_admin(self):
        self.try_destroy(self.nomember, self.mb_admin, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_to_superadmin(self):
        self.try_destroy(self.nomember, self.mb_superadmin, status.HTTP_403_FORBIDDEN)


    def test_destroy_member_to_member(self):
        self.try_destroy(self.member, self.mb_member, status.HTTP_403_OK)
    def test_destroy_member_to_admin(self):
        self.try_destroy(self.member, self.mb_admin, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_to_superadmin(self):
        self.try_destroy(self.member, self.mb_superadmin, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_to_member2(self):
        self.try_destroy(self.member, self.mb_member2, status.HTTP_403_FORBIDDEN)


    def test_destroy_admin_to_member(self):
        self.try_destroy(self.admin, self.mb_member, status.HTTP_200_OK)
    def test_destroy_admin_to_admin(self):
        self.try_destroy(self.admin, self.mb_admin, status.HTTP_403_OK)
    def test_destroy_admin_to_superadmin(self):
        self.try_destroy(self.admin, self.mb_admin, status.HTTP_403_FORBIDDEN)
    def test_destroy_admin_to_admin2(self):
        self.try_destroy(self.admin, self.mb_admin2, status.HTTP_200_FORBIDDEN)



    def test_destroy_superadmin_to_member(self):
        self.try_destroy(self.superadmin, self.mb_member, status.HTTP_200_OK)
    def test_destroy_superadmin_to_admin(self):
        self.try_destroy(self.superadmin, self.mb_admin, status.HTTP_200_OK)
    def test_destroy_superadmin_to_superadmin(self):
        self.try_destroy(self.superadmin, self.mb_superadmin, status.HTTP_403_FORBIDDEN)


    ###############################################################################################
    ##     RETRIEVE TESTS                                                                        ##
    ###############################################################################################

    def try_retrieve(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.get(self.group_field_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

        if r.status_code == status.HTTP_200_OK:
            self.assertEqual( r.data, GroupFieldSerializer(f).data )

    #FOR NO MEMBER : DEPENDS ON THE TYPE OF THE GROUP AND CONNECTIONS : EASILY IMPLEMENTABLE


    def test_retrieve_member_to_member(self):
        self.try_retrieve(self.member, self.mb_member, status.HTTP_200_OK)
    def test_retrieve_member_to_admin(self):
        self.try_retrieve(self.member, self.mb_admin, status.HTTP_200_OK)
    def test_retrieve_member_to_superadmin(self):
        self.try_retrieve(self.member, self.mb_superadmin, status.HTTP_200_OK)
    def test_retrieve_member_to_member2(self):
        self.try_retrieve(self.member, self.mb_member2, status.HTTP_200_OK)


    def test_retrieve_admin_to_member(self):
        self.try_retrieve(self.admin, self.mb_member, status.HTTP_200_OK)
    def test_retrieve_admin_to_admin(self):
        self.try_retrieve(self.admin, self.mb_admin, status.HTTP_200_OK)
    def test_retrieve_admin_to_superadmin(self):
        self.try_retrieve(self.admin, self.mb_admin, status.HTTP_200_OK)
    def test_retrieve_admin_to_admin2(self):
        self.try_retrieve(self.admin, self.mb_admin2, status.HTTP_200_OK)



    def test_retrieve_superadmin_to_member(self):
        self.try_retrieve(self.superadmin, self.mb_member, status.HTTP_200_OK)
    def test_retrieve_superadmin_to_admin(self):
        self.try_retrieve(self.superadmin, self.mb_admin, status.HTTP_200_OK)
    def test_retrieve_superadmin_to_superadmin(self):
        self.try_retrieve(self.superadmin, self.mb_superadmin, status.HTTP_200_OK)

    ###############################################################################################
    ##     CREATE TESTS                                                                         ##
    ###############################################################################################

    #u the user who wants to create
    #f the user who might become a member
    def try_create(self, u, f, status):
        self.client.force_authenticate(user=u)
        r = self.client.post(self.group_member_url, {'group': self.group.id, 'user': f}, format='json')
        self.assertEqual(r.status_code, status)

    def test_create_nomember_to_nomember(self):
        self.try_create(self.nomember, self.nomember, status.HTTP_403_FORBIDDEN)
    def test_create_member_to_nomember(self):
        self.try_create(self.member, self.nomember, status.HTTP_403_FORBIDDEN)
    def test_create_admin_to_nomember(self):
        self.try_create(self.admin, self.nomember, status.HTTP_403_FORBIDDEN)
    def test_create_super_admin_to_nomember(self):
        self.try_create(self.super_admin, self.nomember, status.HTTP_403_FORBIDDEN)

    def test_create_nomember_to_member(self):
        self.try_create(self.member, self.member, status.HTTP_403_FORBIDDEN)
    def test_create_member_to_member(self):
        self.try_create(self.member, self.member, status.HTTP_403_FORBIDDEN)
    def test_create_admin_to_member(self):
        self.try_create(self.admin, self.member, status.HTTP_403_FORBIDDEN)
    def test_create_super_admin_to_member(self):
        self.try_create(self.super_admin, self.member, status.HTTP_403_FORBIDDEN)
