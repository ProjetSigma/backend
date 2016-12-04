from rest_framework import status
from rest_framework.test import APITestCase

from sigma_core.models.user import User
from sigma_core.models.group import Group
from sigma_core.models.group_member import GroupMember
from sigma_core.models.group_invitation import GroupInvitation
from sigma_core.serializers.group_invitation import GroupInvitationSerializer


class GroupInvitationTests(APITestCase):
    @classmethod
    def setUpTestData(self):
        super(APITestCase, self).setUpTestData()
        self.invitation_url = '/group-invitation/'


        self.askableGroup = Group.objects.create(name="Les gens peuvent demander de rejoindre ce groupe, mais il faut etre accepté", description="")
        self.nonAskableGroup = Group.objects.create(name="Les gens ne peuvent pas demander de rejoindre ce groupe", description="", can_anyone_ask = False)
        self.acceptallGroup = Group.objects.create(name="Groupe qui accepte tout le monde directement", need_validation_to_join=false)

        # Five user type (not a member, asked to join, invited by the group, member, member with can_invite)
        self.nomember = User.objects.create(email='nomember@sigma.fr', lastname='Nomembre', firstname='Bemmonre');
        self.invitee = User.objects.create(email='invitee@sigma.fr', lastname='Invitee', firstname='Neiteiv')
        self.invited = User.objects.create(email='invited@sigma.fr', lastname='Invited', firstname='Nitidev')
        self.member = User.objects.create(email='member@sigma.fr', lastname='Membre', firstname='Remmeb');
        self.admin = User.objects.create(email='admin@sigma.fr', lastname='Admin', firstname='Nimad');

        # Create the related invitations/memberships
        self.invitee_askable = GroupInvitation.objects.create(invitee=self.invitee, group=self.askableGroup, emmited_by_invitee=True)
        self.invited_askable = GroupInvitation.objects.create(invitee=self.invited, group=self.askableGroup, emmited_by_invitee=False)
        self.invited_nonAskable = GroupInvitation.objects.create(invitee=self.invited, group=self.nonAskableGroup, emmited_by_invitee=False)


        GroupMember.objects.create(user=self.member, group=self.askableGroup)
        GroupMember.objects.create(user=self.member, group=self.nonAskableGroup)
        GroupMember.objects.create(user=self.member, group=self.acceptallGroup)

        GroupMember.objects.create(user=self.admin, group=self.askableGroup, can_invite=True)
        GroupMember.objects.create(user=self.admin, group=self.nonAskableGroup, can_invite=True)
        GroupMember.objects.create(user=self.admin, group=self.acceptallGroup, can_invite=True)


    ###############################################################################################
    ##     CREATION TESTS                                                                        ##
    ###############################################################################################

    def try_create(self, user_logged, user, group, emmited_by_invitee, status):
        self.client.force_authenticate(user=user_logged)
        r = self.client.post(self.invitation_url, {'group': group.id, 'invitee': user.id, 'emmited_by_invitee': emmited_by_invitee}, format='json')
        self.assertEqual(r.status_code, status)

    # User asking to join
    # Change according to the fact that the group can directly accept members
    def test_create_nomember_in_askablegr(self):
        self.try_create(self.nomember, self.nomember, self.askableGroup, True, status.HTTP_201_CREATED)
    def test_create_nomember_in_nonAskablegr(self):
        self.try_create(self.nomember, self.nomember, self.nonAskableGroup, True, status.HTTP_403_FORBIDDEN)
    def test_create_nomember_in_acceptallgr(self):
        self.try_create(self.nomember, self.nomember, self.acceptallGroup, True, status.HTTP_201_CREATED)

    def test_create_invitee_in_askablegr(self):
        self.try_create(self.invitee, self.invitee, self.askableGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_invitee_in_nonAskablegr(self):
        self.try_create(self.invitee, self.invitee, self.nonAskableGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_invitee_in_acceptallgr(self):
        self.try_create(self.invitee, self.invitee, self.acceptallGroup, True, status.HTTP_400_BAD_REQUEST)

    def test_create_member_in_askablegr(self):
        self.try_create(self.member, self.member, self.askableGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_member_in_nonAskablegr(self):
        self.try_create(self.member, self.member, self.nonAskableGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_member_in_acceptallgr(self):
        self.try_create(self.member, self.member, self.acceptallGroup, True, status.HTTP_400_BAD_REQUEST)


    # User being invited

    def test_nomember_invite_nomember_in_askablegr(self):
        self.try_create(self.nomember, self.nomember, self.askableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_nomember_invite_nomember_in_askablegr(self):
        self.try_create(self.nomember, self.nomember, self.nonAskableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_nomember_invite_nomember_in_askablegr(self):
        self.try_create(self.nomember, self.nomember, self.acceptallGroup, False, status.HTTP_403_FORBIDDEN)

    def test_invitee_invite_nomember_in_askablegr(self):
        self.try_create(self.invitee, self.nomember, self.askableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_invitee_invite_nomember_in_askablegr(self):
        self.try_create(self.invitee, self.nomember, self.nonAskableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_invitee_invite_nomember_in_askablegr(self):
        self.try_create(self.invitee, self.nomember, self.acceptallGroup, False, status.HTTP_403_FORBIDDEN)

    def test_member_invite_nomember_in_askablegr(self):
        self.try_create(self.member, self.nomember, self.askableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_member_invite_nomember_in_askablegr(self):
        self.try_create(self.member, self.nomember, self.nonAskableGroup, False, status.HTTP_403_FORBIDDEN)
    def test_member_invite_nomember_in_askablegr(self):
        self.try_create(self.member, self.nomember, self.acceptallGroup, False, status.HTTP_403_FORBIDDEN)

    def test_admin_invite_nomember_in_askablegr(self):
        self.try_create(self.admin, self.nomember, self.askableGroup, False, status.HTTP_201_CREATED)
    def test_admin_invite_nomember_in_askablegr(self):
        self.try_create(self.admin, self.nomember, self.nonAskableGroup, False, status.HTTP_201_CREATED)
    def test_admin_invite_nomember_in_askablegr(self):
        self.try_create(self.admin, self.nomember, self.acceptallGroup, False, status.HTTP_201_CREATED)








    ##############################################################################################
    #     RETRIEVE TESTS                                                                        ##
    ##############################################################################################

    def try_retrieve(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.get(self.invitation_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

        if r.status_code == status.HTTP_200_OK:
            self.assertEqual( r.data, GroupFieldSerializer(f).data )


    def test_retrieve_nomember_in_invitee_askable(self):
        self.try_retrieve(self.nomember, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_retrieve_nomember_in_invited_askable(self):
        self.try_retrieve(self.nomember, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_retrieve_nomember_in_invited_nonAskable(self):
        self.try_retrieve(self.nomember, self.invitee_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_retrieve_member_in_invitee_askable(self):
        self.try_retrieve(self.member, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_retrieve_member_in_invited_askable(self):
        self.try_retrieve(self.member, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_retrieve_member_in_invited_nonAskable(self):
        self.try_retrieve(self.member, self.invited_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_retrieve_invitee_in_invitee_askable(self):
        self.try_retrieve(self.invitee, self.invitee_askable, status.HTTP_200_OK)
    def test_retrieve_invited_in_invited_askable(self):
        self.try_retrieve(self.invited, self.invited_askable, status.HTTP_200_OK)
    def test_retrieve_invited_in_invited_nonAskable(self):
        self.try_retrieve(self.invited, self.invited_nonAskable, status.HTTP_200_OK)

    def test_retrieve_admin_in_invitee_askable(self):
        self.try_retrieve(self.admin, self.invitee_askable, status.HTTP_200_OK)
    def test_retrieve_admin_in_invited_askable(self):
        self.try_retrieve(self.admin, self.invited_askable, status.HTTP_200_OK)
    def test_retrieve_admin_in_invited_nonAskable(self):
        self.try_retrieve(self.admin, self.invited_nonAskable, status.HTTP_200_OK)


    ##############################################################################################
    #     DESTROY TESTS                                                                        ##
    ##############################################################################################

    def try_destroy(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.get(self.invitation_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

        if r.status_code == status.HTTP_200_OK:
            self.assertEqual( r.data, GroupFieldSerializer(f).data )


    def test_destroy_nomember_in_invitee_askable(self):
        self.try_destroy(self.nomember, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_in_invited_askable(self):
        self.try_destroy(self.nomember, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_destroy_nomember_in_invited_nonAskable(self):
        self.try_destroy(self.nomember, self.invitee_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_destroy_member_in_invitee_askable(self):
        self.try_destroy(self.member, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_in_invited_askable(self):
        self.try_destroy(self.member, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_destroy_member_in_invited_nonAskable(self):
        self.try_destroy(self.member, self.invited_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_destroy_invitee_in_invitee_askable(self):
        self.try_destroy(self.invitee, self.invitee_askable, status.HTTP_200_OK)
    def test_destroy_invited_in_invited_askable(self):
        self.try_destroy(self.invited, self.invited_askable, status.HTTP_200_OK)
    def test_destroy_invited_in_invited_nonAskable(self):
        self.try_destroy(self.invited, self.invited_nonAskable, status.HTTP_200_OK)

    def test_destroy_admin_in_invitee_askable(self):
        self.try_destroy(self.admin, self.invitee_askable, status.HTTP_200_OK)
    def test_destroy_admin_in_invited_askable(self):
        self.try_destroy(self.admin, self.invited_askable, status.HTTP_200_OK)
    def test_destroy_admin_in_invited_nonAskable(self):
        self.try_destroy(self.admin, self.invited_nonAskable, status.HTTP_200_OK)

    ##############################################################################################
    #     CONFIRM TESTS                                                                        ##
    ##############################################################################################

    def try_confirm(self, u, f, s):
        self.client.force_authenticate(user=u)
        r = self.client.get(self.invitation_url + str(f.id) + '/', format='json')
        self.assertEqual(r.status_code, s)

        if r.status_code == status.HTTP_200_OK:
            self.assertEqual( r.data, GroupFieldSerializer(f).data )


    def test_confirm_nomember_in_invitee_askable(self):
        self.try_confirm(self.nomember, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_nomember_in_invited_askable(self):
        self.try_confirm(self.nomember, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_nomember_in_invited_nonAskable(self):
        self.try_confirm(self.nomember, self.invitee_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_confirm_member_in_invitee_askable(self):
        self.try_confirm(self.member, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_member_in_invited_askable(self):
        self.try_confirm(self.member, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_member_in_invited_nonAskable(self):
        self.try_confirm(self.member, self.invited_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_confirm_invitee_in_invitee_askable(self):
        self.try_confirm(self.invitee, self.invitee_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_invited_in_invited_askable(self):
        self.try_confirm(self.invited, self.invited_askable, status.HTTP_403_FORBIDDEN)
    def test_confirm_invited_in_invited_nonAskable(self):
        self.try_confirm(self.invited, self.invited_nonAskable, status.HTTP_403_FORBIDDEN)

    def test_confirm_admin_in_invitee_askable(self):
        self.try_confirm(self.admin, self.invitee_askable, status.HTTP_200_OK)
    def test_confirm_admin_in_invited_askable(self):
        self.try_confirm(self.admin, self.invited_askable, status.HTTP_200_OK)
    def test_confirm_admin_in_invited_nonAskable(self):
        self.try_confirm(self.admin, self.invited_nonAskable, status.HTTP_200_OK)
