"""Rides permissions"""


from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify requesting user is the creator of the ride"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.offered_by
