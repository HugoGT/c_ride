"""Membership serializers"""


from rest_framework import serializers

from cride.circles.models import Membership
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
