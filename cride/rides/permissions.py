"""Rides permissions"""


from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify requesting user is the creator of the ride"""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.offered_by


class IsNotRideOwner(BasePermission):
    """Only users that aren't ride owner can call the views"""

    def has_object_permission(self, request, view, obj):
        return not request.user == obj.offered_by
