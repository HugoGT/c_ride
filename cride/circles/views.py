"""Circles views"""


from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from cride.circles.models import Circle, Membership
from cride.circles.permissions import IsCircleAdmin
from cride.serializers import CircleModelSerializer, MembershipModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    lookup_field = 'slug_name'
    serializer_class = CircleModelSerializer

    def get_queryset(self):
        """Only lists public circles"""
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.filter(is_public=True)
        return queryset

    def perform_create(self, seralizer):
        """Assign circle admin"""
        circle = seralizer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )

    def destroy(self, request, pk=None):
        """No one can delete a circle"""
        raise MethodNotAllowed('DELETE')

    def get_permissions(self):
        """Assign permissionss based on action"""
        permissions = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions]


class MembershipViewSet(viewsets.ModelViewSet):
    """Circle membership viewset"""

    serializer_class = MembershipModelSerializer

    def dispatch(self, request, *args, **kwargs):
        """Verify that the circle exists"""
        slug_name = kwargs['slug_name']
        self.circle = get_object_or_404(Circle, slug_name=slug_name)

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return circle members"""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )
