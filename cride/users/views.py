"""Users views"""


from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cride.serializers import (
    UserModelSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    UserVerificationSerializer
    )

from cride.circles.models import Circle
from cride.serializers import CircleModelSerializer, ProfileModelSerializer
from cride.users.models import User
from cride.users.permissions import IsAccountOwner


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    """
    User view set

    Handle user details. A user can only see his own details.
    """

    queryset = User.objects.filter(is_active=True, is_client=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        """Assign permissions"""
        if self.action == 'retrieve':
            permissions = [IsAuthenticated()]
        else:
            permissions = [IsAuthenticated(), IsAccountOwner()]

        return permissions

    def retrieve(self, request, *args, **kwargs):
        """Add extra data to the response"""
        response = super().retrieve(request, *args, **kwargs)
        circles = Circle.objects.filter(
            members=request.user,
            membership__is_active=True
        )
        data = {
            'user': response.data,
            'belongs_to': str(circles.count()) + ' circles',
            'circles_member': CircleModelSerializer(circles.filter(is_public=True), many=True).data
        }
        response.data = data

        return response

    @action(detail=True, methods=['put', 'patch'])
    def profile(self, request, *args, **kwargs):
        """Update profile data"""
        user = self.get_object()
        profile = user.profile
        partial = request.method == 'PATCH'
        serializer = ProfileModelSerializer(
            profile,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = UserModelSerializer(user).data

        return Response(data)


class AuthViewSet(viewsets.GenericViewSet):
    """Auth view set

    Handle sign up, login and account  verification
    """

    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User sign up"""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token,
        }

        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify user sign up token"""
        serializer = UserVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'message': 'Congratulation, now go share some rides!'},
            status=status.HTTP_200_OK
            )
