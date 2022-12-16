"""Users views"""


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cride.serializers import (
    UserModelSerializer,
    UserLoginSerializer,
    UserSignupSerializer,
    UserVerificationSerializer
    )


class UserSignupAPIView(APIView):
    """User sign up API view"""

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request"""
        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserModelSerializer(user).data

        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginAPIView(APIView):
    """User login API view"""

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        data = {
            'user': UserModelSerializer(user).data,
            'access_token': token,
        }

        return Response(data, status=status.HTTP_201_CREATED)


class UserVerifyAPIView(APIView):
    """Account verify view"""

    def post(self, request, *args, **kwargs):
        """Handle HTTP POST request"""
        serializer = UserVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message': 'Congratulation, now go share some rides!'}, status=status.HTTP_200_OK)
