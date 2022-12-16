"""Users Serializers"""


from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from cride.users.models import User


class UserModelSerializer(serializers.ModelSerializer):
    """User model serializer"""

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'last_name',
            'first_name',
            'phone_number'
        )


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
        self.context['user'] = user

        return data

    def create(self, data):
        """Create a token to identify the user and update the last login date"""
        token, created_token = Token.objects.get_or_create(user=self.context['user'])

        user = self.context['user']
        if created_token:
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

        return user, token.key
