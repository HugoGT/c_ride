"""Users views"""


from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from cride.serializers import (
    UserModelSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    UserVerificationSerializer
    )


class UserViewSet(viewsets.GenericViewSet):
    """User view set

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
