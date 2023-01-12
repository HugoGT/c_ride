"""Rides views"""


from django.utils.timezone import localtime, now, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cride.circles.models import Circle
from cride.circles.permissions import IsActiveCircleMember
from cride.rides.permissions import IsRideOwner
from cride.serializers import CreateRideSerializer, RideModelSerializer, JoinRideSerializer


class RideViewSet(viewsets.ModelViewSet):
    """Ride view set"""

    filter_backends = (SearchFilter, OrderingFilter)
    ordering = ('departure_date', 'arrival_date', 'available_seats')
    ordering_fields = ('departure_date', 'arrival_date', 'available_seats')
    search_fields = ('departure_location', 'arrival_location')

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated, IsActiveCircleMember]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsRideOwner)

        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return active circle's rides"""
        offset = localtime(now()) + timedelta(minutes=20)

        return self.circle.ride_set.filter(
            departure_date__gte=offset,
            is_active=True,
            available_seats__gte=1
        )

    def get_serializer_class(self):
        """Return serializer based on action"""
        if self.action == 'create':
            return CreateRideSerializer
        if self.action == 'update':
            return JoinRideSerializer

        return RideModelSerializer

    def get_serializer_context(self):
        """Add circle to serializer context."""

        context = super(RideViewSet, self).get_serializer_context()
        context['circle'] = self.circle

        return context

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)

        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def destroy(self, request, slug_name=None):
        """No one can delete a ride"""
        raise MethodNotAllowed('DELETE')

    @action(detail=True, methods=['post'])
    def join(self, request, *args, **kwargs):
        """Add requesting user to ride"""
        ride = self.get_object()
        serializer = JoinRideSerializer(
            ride,
            data={'passenger': request.user.pk},
            context={'ride': ride, 'circle': self.circle},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        ride = serializer.save()
        data = RideModelSerializer(ride).data

        return Response(data, status=status.HTTP_200_OK)
