"""Rides serializers"""


from django.db import transaction
from django.utils.timezone import localtime, now, timedelta
from rest_framework import serializers

from cride.circles.models import Membership
from cride.rides.models import Ride
from cride.serializers import UserModelSerializer


class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField(read_only=True)

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        model = Ride
        fields = '__all__'

    def update(self, instance, data):
        """Allow updates only before departure date"""
        time = localtime(now())
        if instance.departure_date <= time:
            raise serializers.ValidationError('Ongoing rides cannot be modified.')

        return super().update(instance, data)


class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride serializer"""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=14)

    class Meta:
        model = Ride
        exclude = ('offered_in', 'passengers', 'rating', 'is_active')

    def validate_departure_date(self, data):
        """Verify date is not in the past"""
        min_date = localtime(now()) + timedelta(minutes=20)
        if data < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least pass the next 20 minutes window.'
            )

        return data

    def validate(self, data):
        """Validate

        Verify that the person who offers the ride is member and also the same user making the request.
        """
        user = data['offered_by']
        circle = self.context['circle']

        if self.context['request'].user != user:
            raise serializers.ValidationError('Rides offered on behalf of others are not allowed.')

        try:
            membership = Membership.objects.get(
                user=user,
                circle=circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle.')

        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidationError('Departure date must happen before arrival date.')

        self.context['membership'] = membership
        return data

    def create(self, data):
        """Create ride and update stats."""

        with transaction.atomic():
            circle = self.context['circle']
            ride = Ride.objects.create(**data, offered_in=circle)

            # Circle
            circle.rides_offered += 1
            circle.save()

            # Membership
            membership = self.context['membership']
            membership.rides_offered += 1
            membership.save()

            # Profile
            profile = data['offered_by'].profile
            profile.rides_offered += 1
            profile.save()

            return ride
