"""Circles views"""


from rest_framework import viewsets

from cride.circles.models import Circle
from cride.serializers import CircleModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer
