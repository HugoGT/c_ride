"""Invitations tests"""


from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from cride.circles.models import Circle, Invitation, Membership
from cride.users.models import User, Profile


class InvitationsManagerTestCase(TestCase):
    """Invitations manager test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@gmail.com',
            username='pablotrinidad',
            password='adm23in123'
        )
        self.circle = Circle.objects.create(
            name='FAC',
            slug_name='fciencias',
            about='Grupo oficial de la FAC',
            verified=True
        )

    def test_code_generation(self):
        """Random codes should be generated automatically"""
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        )

        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one"""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )

        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicated(self):
        """If given code is not unique, a new one must be generated"""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        ).code

        # Create another invitation with the past code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )

        self.assertNotEqual(invitation.code, code)


class MemberInvitationsAPITestCase(APITestCase):
    """Memebr invitation API test case"""

    def setUp(self):
        """Test case setup"""
        self.user = User.objects.create(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@gmail.com',
            username='pablotrinidad',
            password='adm23in123'
        )
        self.profile = Profile.objects.create(user=self.user)
        self.circle = Circle.objects.create(
            name='FAC',
            slug_name='fciencias',
            about='Grupo oficial de la FAC',
            verified=True
        )
        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.profile,
            circle=self.circle,
            remaining_invitations=10
        )
        self.token = Token.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token}')
        self.url = f'/circles/{self.circle.slug_name}/members/{self.user.username}/invitations/'
        self.request = self.client.get(self.url)

    def test_success(self):
        """Verify request succeed"""
        self.assertEqual(self.request.status_code, status.HTTP_200_OK)

    def test_invitation_creation(self):
        """Verify invitation are generated if none exist previously"""
        # Call member invitations URL
        self.assertEqual(self.request.status_code, status.HTTP_200_OK)

        # Verify new invitations were created
        invitations = Invitation.objects.filter(issued_by=self.user)
        self.assertEqual(invitations.count(), self.membership.remaining_invitations)

        for invitation in invitations:
            self.assertIn(invitation.code, self.request.data['invitations'])
