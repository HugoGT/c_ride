"""Circles views"""


from rest_framework import viewsets

from cride.circles.models import Circle
from cride.serializers import CircleModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    queryset = Circle.objects.all()
    serializer_class = CircleModelSerializer

    def get_queryset(self):
        """Only lists public circles"""
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(is_public=True)
        return queryset
