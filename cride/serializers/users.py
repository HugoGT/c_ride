"""Users Serializers"""


from django.contrib.auth import authenticate
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    """User login serializer

    Handle the login request data.
    """

    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Verify credentials"""
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')

        return data
