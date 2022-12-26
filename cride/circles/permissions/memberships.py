"""Membership permissions"""

from rest_framework.permissions import BasePermission

from cride.circles.models import Membership


class IsActiveCircleMember(BasePermission):
    """Allow access only to active circle members

    Expect that the views implementing this permission have a 'circle' attribute assigned.
    """

    def has_permission(self, request, view):
        """Verify user is an actvive member of the circle"""
        try:
            Membership.objects.get(
                circle=view.circle,
                user=request.user,
                is_active=True
            )
        except Membership.DoesNotExist:
            return False

        return True
