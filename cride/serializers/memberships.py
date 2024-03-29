"""Membership serializers"""


from django.utils.timezone import localtime, now
from rest_framework import serializers

from cride.circles.models import Membership, Invitation
from .users import UserModelSerializer


class MembershipModelSerializer(serializers.ModelSerializer):
    """Memeber model serializer"""

    user = UserModelSerializer(read_only=True)
    invited_by = serializers.StringRelatedField()
    joined_at = serializers.DateTimeField(source='created', read_only=True)

    class Meta:
        model = Membership

        fields = (
            'user',
            'is_admin',
            'is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
            'joined_at'
        )
        read_only_fields = (
            'user',
            'invited_by',
            'used_invitations',
            'rides_offered',
            'rides_taken'
        )


class AddMemberSerializer(serializers.Serializer):
    """Add member serializer

    Handle the addition of a new member to a circle, Circle object must be provided in the context.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    invitation_code = serializers.CharField(min_length=8)

    def validate_user(self, data):
        """Verify user isn't already a member"""
        circle = self.context['circle']
        user = data
        q = Membership.objects.filter(circle=circle, user=user)
        if q.exists():
            raise serializers.ValidationError('User is already member of this circle')
        return data

    def validate_invitation_code(self, data):
        """Verify code exists and that it is related to the circle"""
        try:
            invitation = Invitation.objects.get(
                code=data,
                circle=self.context['circle'],
                used=False
            )
        except Invitation.DoesNotExist:
            raise serializers.ValidationError('Invalid invitation code.')
        self.context['invitation'] = invitation
        return data

    def validate(self, data):
        """Verify circle is capable of accepting a new member"""
        circle = self.context['circle']
        if circle.is_limited and circle.members.count() >= circle.members_limit:
            raise serializers.ValidationError('Circle has reached its member limit :(')
        return data

    def create(self, data):
        """Create new circle member"""
        invitation = self.context['invitation']
        circle = self.context['circle']
        user = data['user']

        time = localtime(now())

        # Member creation
        member = Membership.objects.create(
            user=user,
            profile=user.profile,
            circle=circle,
            invited_by=invitation.issued_by
        )

        # Update Invitation
        invitation.used_by = user
        invitation.used = True
        invitation.used_at = time
        invitation.save()

        # Update issuer data
        issuer = Membership.objects.get(user=invitation.issued_by, circle=circle)
        issuer.used_invitations += 1
        issuer.remaining_invitations -= 1
        issuer.save()

        return member
