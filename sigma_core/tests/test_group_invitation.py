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

        # Three groups by accessability
        self.privateGroup = Group.objects.create(name="Groupe privé", description="")
        self.normalGroup = Group.objects.create(name="Groupe normal", description="")
        self.searchableGroup = Group.objects.create(name="Groupe cherchable", description="")

        # Five user type (not a member, asked to join, invited by the group, member, member with can_invite)
        self.nomember = User.objects.create(email='nomember@sigma.fr', lastname='Nomembre', firstname='Bemmonre');
        self.invitee = User.objects.create(email='invitee@sigma.fr', lastname='Invitee', firstname='Neiteiv')
        self.invited = User.objects.create(email='invited@sigma.fr', lastname='Invited', firstname='Nitidev')
        self.member = User.objects.create(email='member@sigma.fr', lastname='Membre', firstname='Remmeb');
        self.admin = User.objects.create(email='admin@sigma.fr', lastname='Admin', firstname='Nimad');

        # Create the related invitations/memberships
        GroupInvitation.objects.create(invitee=self.invitee, group=self.privateGroup, emmited_by_invitee=True)
        GroupInvitation.objects.create(invitee=self.invitee, group=self.normalGroup, emmited_by_invitee=True)
        GroupInvitation.objects.create(invitee=self.invitee, group=self.searchableGroup, emmited_by_invitee=True)

        GroupInvitation.objects.create(invitee=self.invited, group=self.privateGroup, emmited_by_invitee=False)
        GroupInvitation.objects.create(invitee=self.invited, group=self.normalGroup, emmited_by_invitee=False)
        GroupInvitation.objects.create(invitee=self.invited, group=self.searchableGroup, emmited_by_invitee=False)

        GroupMember.objects.create(user=self.member, group=self.privateGroup)
        GroupMember.objects.create(user=self.member, group=self.normalGroup)
        GroupMember.objects.create(user=self.member, group=self.searchableGroup)

        GroupMember.objects.create(user=self.admin, group=self.privateGroup, can_invite=True)
        GroupMember.objects.create(user=self.admin, group=self.normalGroup, can_invite=True)
        GroupMember.objects.create(user=self.admin, group=self.searchableGroup, can_invite=True)


    ###############################################################################################
    ##     CREATION TESTS                                                                        ##
    ###############################################################################################

    def try_create(self, user_logged, user, group, emmited_by_invitee, status):
        self.client.force_authenticate(user=user_logged)
        r = self.client.post(self.invitation_url, {'group': group.id, 'invitee': user.id, 'emmited_by_invitee': emmited_by_invitee}, format='json')
        self.assertEqual(r.status_code, status)

    # User asking to join
    # Change according to the fact that the group can directly accept members
    def test_create_nomember_in_privategr(self):
        self.try_create(self.nomember, self.nomember, self.privateGroup, True, status.HTTP_403_FORBIDDEN)
    def test_create_nomember_in_normalgr(self):
        self.try_create(self.nomember, self.nomember, self.normalGroup, True, status.HTTP_403_FORBIDDEN)
    def test_create_nomember_in_searchablegr(self):
        self.try_create(self.nomember, self.nomember, self.searchableGroup, True, status.HTTP_201_CREATED)

    def test_create_invitee_in_privategr(self):
        self.try_create(self.invitee, self.invitee, self.privateGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_invitee_in_normalgr(self):
        self.try_create(self.invitee, self.invitee, self.normalGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_invitee_in_searchablegr(self):
        self.try_create(self.invitee, self.invitee, self.searchableGroup, True, status.HTTP_400_BAD_REQUEST)

    def test_create_member_in_privategr(self):
        self.try_create(self.invitee, self.invitee, self.privateGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_member_in_normalgr(self):
        self.try_create(self.invitee, self.invitee, self.normalGroup, True, status.HTTP_400_BAD_REQUEST)
    def test_create_member_in_searchablegr(self):
        self.try_create(self.invitee, self.invitee, self.searchableGroup, True, status.HTTP_400_BAD_REQUEST)


    # User being invited

    def test_nomember_invite_nomember_in_privategr(self):
        self.try_create(self.nomember, self.nomember, self.privateGroup, False, status.HTTP_403_FORBIDDEN)
    def test_nomember_invite_nomember_in_privategr(self):
        self.try_create(self.nomember, self.nomember, self.normalGroup, False, status.HTTP_403_FORBIDDEN)
    def test_nomember_invite_nomember_in_privategr(self):
        self.try_create(self.nomember, self.nomember, self.searchableGroup, False, status.HTTP_403_FORBIDDEN)

    def test_invitee_invite_nomember_in_privategr(self):
        self.try_create(self.invitee, self.nomember, self.privateGroup, False, status.HTTP_403_FORBIDDEN)
    def test_invitee_invite_nomember_in_privategr(self):
        self.try_create(self.invitee, self.nomember, self.normalGroup, False, status.HTTP_403_FORBIDDEN)
    def test_invitee_invite_nomember_in_privategr(self):
        self.try_create(self.invitee, self.nomember, self.searchableGroup, False, status.HTTP_403_FORBIDDEN)

    def test_member_invite_nomember_in_privategr(self):
        self.try_create(self.member, self.nomember, self.privateGroup, False, status.HTTP_403_FORBIDDEN)
    def test_member_invite_nomember_in_privategr(self):
        self.try_create(self.member, self.nomember, self.normalGroup, False, status.HTTP_403_FORBIDDEN)
    def test_member_invite_nomember_in_privategr(self):
        self.try_create(self.member, self.nomember, self.searchableGroup, False, status.HTTP_403_FORBIDDEN)

    def test_admin_invite_nomember_in_privategr(self):
        self.try_create(self.admin, self.nomember, self.privateGroup, False, status.HTTP_201_CREATED)
    def test_admin_invite_nomember_in_privategr(self):
        self.try_create(self.admin, self.nomember, self.normalGroup, False, status.HTTP_201_CREATED)
    def test_admin_invite_nomember_in_privategr(self):
        self.try_create(self.admin, self.nomember, self.searchableGroup, False, status.HTTP_201_CREATED)








    ###############################################################################################
    ##     RETRIEVE TESTS                                                                        ##
    ###############################################################################################

    # def try_retrieve(self, u, f, s):
        # self.client.force_authenticate(user=u)
        # r = self.client.get(self.group_field_url + str(f.id) + '/', format='json')
        # self.assertEqual(r.status_code, s)

        # if r.status_code == status.HTTP_200_OK:
            # self.assertEqual( r.data, GroupFieldSerializer(f).data )


    # def test_retrieve_nomember_in_secretgr(self):
        # self.try_retrieve(self.nomember, self.secretGroupField, status.HTTP_403_FORBIDDEN)
    # def test_retrieve_nomember_in_normalgr(self):
        # self.try_retrieve(self.nomember, self.normalGroupField, status.HTTP_200_OK)
    # def test_retrieve_nomember_in_publicgr(self):
        # self.try_retrieve(self.nomember, self.publicGroupField, status.HTTP_200_OK)

    # def test_retrieve_member_in_secretgr(self):
        # self.try_retrieve(self.member, self.secretGroupField, status.HTTP_200_OK)
    # def test_retrieve_member_in_normalgr(self):
        # self.try_retrieve(self.member, self.normalGroupField, status.HTTP_200_OK)
    # def test_retrieve_member_in_publicgr(self):
        # self.try_retrieve(self.member, self.publicGroupField, status.HTTP_200_OK)

    # def test_retrieve_admin_in_secretgr(self):
        # self.try_retrieve(self.admin, self.secretGroupField, status.HTTP_200_OK)
    # def test_retrieve_admin_in_normalgr(self):
        # self.try_retrieve(self.admin, self.normalGroupField, status.HTTP_200_OK)
    # def test_retrieve_admin_in_publicgr(self):
        # self.try_retrieve(self.admin, self.publicGroupField, status.HTTP_200_OK)
