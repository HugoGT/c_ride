"""Rides serializers"""


from django.db import transaction
from django.utils.timezone import localtime, now, timedelta
from rest_framework import serializers

from cride.circles.models import Membership
from cride.rides.models import Ride
from cride.users.models import User
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


class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer"""

    passenger = serializers.IntegerField()

    class Meta:
        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, data):
        """Verify passenger exists and is a circle member"""
        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid passenger.')

        circle = self.context['circle']
        try:
            membership = Membership.objects.get(
                user=user,
                circle=circle,
                is_active=True
            )
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle.')

        self.context['user'] = user
        self.context['member'] = membership

        return data

    def validate(self, data):
        """Verify rides allow new passengers"""
        ride = self.context['ride']
        if ride.departure_date <= localtime(now()):
            raise serializers.ValidationError("You can't join this ride now.")

        if ride.available_seats < 1:
            raise serializers.ValidationError("Ride is already full.")

        if ride.passengers.filter(pk=self.context['user'].pk).exists():
            raise serializers.ValidationError("Passenger is already on this trip.")

        return data

    def update(self, instance, data):
        """Add passenger to ride, and update stats"""
        ride = self.context['ride']
        user = self.context['user']
        circle = self.context['circle']
        member = self.context['member']
        profile = user.profile

        with transaction.atomic():
            ride.passengers.add(user)
            ride.availiable_seats -= 1
            ride.save()

            #Profile
            profile.rides_taken += 1
            profile.save()

            #Membreship
            member.rides_taken += 1
            member.save()

            #Circle
            circle.rides_taken += 1
            circle.save()

            return ride


class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer"""

    current_time = serializers.DateTimeField()

    class Meta:
        model = Ride
        fields = ('is_active', 'current_time')

    def validate_current_time(self, data):
        """Verify ride have indeed started"""
        ride = self.context['view'].get_object()
        if ride.departure_date >= data:
            raise serializers.ValidationError('Ride has not started yet.')

        return data
