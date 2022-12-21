"""Circles serializers"""


from rest_framework import serializers

from cride.circles.models import Circle


class CircleModelSerializer(serializers.ModelSerializer):
    """Circle model serializer"""

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
