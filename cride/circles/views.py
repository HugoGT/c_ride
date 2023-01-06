"""Circles views"""


from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cride.circles.models import Circle, Invitation, Membership
from cride.circles.permissions import IsActiveCircleMember, IsCircleAdmin, IsSelfMember
from cride.serializers import AddMemberSerializer, CircleModelSerializer, MembershipModelSerializer


class CircleViewSet(viewsets.ModelViewSet):
    """Circle view set"""

    lookup_field = 'slug_name'
    serializer_class = CircleModelSerializer

    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('slug_name', 'name')
    ordering_fields = ('rides_offered', 'rides_taken', 'name', 'created', 'members_limit')
    ordering = ('-members__count', '-rides_offered', '-rides_taken')
    filter_fields = ('verified', 'is_limited')


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

    def destroy(self, request, slug_name=None):
        """No one can delete a circle"""
        raise MethodNotAllowed('DELETE')

    def get_permissions(self):
        """Assign permissionss based on action"""
        if self.action is 'get':
            return []
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

    def create(self, request, *args, **kwargs):
        """Handle member creation from invitation code."""
        serializer = AddMemberSerializer(
            data=request.data,
            context={'circle': self.circle, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        data = self.get_serializer(member).data

        return Response(data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """Disable membership"""
        instance.is_active = False
        instance.save()

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated]
        if self.action != 'create':
            permissions.append(IsActiveCircleMember)
        if self.action == 'invitations':
            permissions.append(IsSelfMember)
        return [permission() for permission in permissions]

    def get_queryset(self):
        """Return circle members"""
        return Membership.objects.filter(
            circle=self.circle,
            is_active=True
        )

    def get_object(self):
        """Return the circle member by using the user's username"""
        return get_object_or_404(
            Membership,
            user__username=self.kwargs['pk'],
            circle=self.circle,
            is_active=True
        )

    @action(detail=True, methods=['get'])
    def invitations(self, request, *args, **kwargs):
        """Retrieve a member's invitations breakdown

        Will return a list containing all the members that have used its invitations and onather list containing the invitations that haven't being used yet.
        """
        member = self.get_object()
        invited_members = Membership.objects.filter(
            circle=self.circle,
            invited_by=request.user,
            is_active=True
        )
        unused_invitations = Invitation.objects.filter(
            circle=self.circle,
            issued_by=request.user,
            used=False
        ).values_list('code')
        diff = member.remaining_invitations - unused_invitations.count()

        invitations = [x[0] for x in unused_invitations]
        for i in range(0, diff):
            invitations.append(
                Invitation.objects.create(
                    issued_by=request.user,
                    circle=self.circle
                ).code
            )

        data = {
            'used_intivations': MembershipModelSerializer(invited_members, many=True).data,
            'invitations': invitations,
        }

        return Response(data)
