"""Circles serializers"""


from rest_framework import serializers

from cride.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """Circle model serializer"""

    members_limit = serializers.IntegerField(
        required=False,
        min_value=10,
        max_value=256,
    )
    is_limited = serializers.BooleanField(default=False)

    class Meta:
        model = Circle
        fields = (
            'name',
            'slug_name',
            'rides_taken',
            'rides_offered',
            'members_limit',
            'is_limited',
            'is_public',
            'verified',
            'picture',
            'about',
        )
        read_only_fields = (
            'rides_offered',
            'rides_taken'
        )

    def validate(self, data):
        """Ensure both members_limit and is_limited are present"""
        method = self.context['request'].method
        if method == 'POST':
            members_limit = data.get('members_limit', None)
            is_limited = data.get('is_limited', False)
        if is_limited ^ bool(members_limit):
            raise serializers.ValidationError('If circle is limited, a members limit must be provided')
        return data

