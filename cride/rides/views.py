"""Rides views"""


from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from cride.circles.models import Circle
from cride.circles.permissions import IsActiveCircleMember
from cride.serializers import CreateRideSerializer


class RideViewSet(viewsets.ModelViewSet):
    """Ride view set"""

    serializer_class = CreateRideSerializer
    permission_classes = [IsAuthenticated, IsActiveCircleMember]

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists."""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)

        return super(RideViewSet, self).dispatch(request, *args, **kwargs)

    def destroy(self, request, slug_name=None):
        """No one can delete a ride"""
        raise MethodNotAllowed('DELETE')
