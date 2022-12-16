"""Users Serializers"""


import jwt

from django.conf import settings
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator

from cride.users.models import User, Profile


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


class UserSignupSerializer(serializers.Serializer):
    """User sign up serializer

    Handle sign up data validation and profile creation.
    """

    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            ]
        )
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators=[
            UniqueValidator(queryset=User.objects.all())
            ],
    )

    last_name = serializers.CharField(min_length=2, max_length=40)
    first_name = serializers.CharField(min_length=2, max_length=40)

    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +987654321'
    )
    phone_number = serializers.CharField(
        min_length=8,
        max_length=16,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            phone_regex,
            ],
    )

    password = serializers.CharField(min_length=8, max_length=64)
    password_confirmation = serializers.CharField(min_length=8, max_length=64)

    def validate(self, data):
        """Verify passwords match"""
        passwd = data['password']
        passwd_conf = data['password_confirmation']
        if passwd != passwd_conf:
            raise serializers.ValidationError({
                "password_confirmation": "Passwords don't match."
                })

        password_validation.validate_password(passwd)
        data['password'] = make_password(passwd)

        return data

    def create(self, data):
        """Handle user and profile creation"""
        data.pop('password_confirmation')
        user = User.objects.create(**data, is_verified=True) # is_verified = changes to True in production
        Profile.objects.create(user=user)

        return user

    def send_confirmation_email(self, user):
        """Sends a link to verify users account"""
        verification_token = self.gen_verification_token(user)
        subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
        from_email = 'Comparte Ride <noreply@comparteride.com>'
        content = render_to_string(
            'emails/users/account_verification.html',
            {'token': verification_token, 'user': user}
        )
        msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
        msg.attach_alternative(content, "text/html")
        msg.send()

    def gen_verification_token(self, user):
        """Create JSON Web Token that the user can use to verify its account"""
        exp_date = timezone.now() + timezone.timedelta(days=2)
        payload = {
            'user': user.username,
            'exp': int(exp_date.timestamp()),
            'type': 'email_confirmation'
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return token


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
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_verified:
            raise serializers.ValidationError('Account is not active yet, please check your email.')
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


class UserVerificationSerializer(serializers.Serializer):
    """Account verification serializer

    Receives a token and decode it to verify the user's account.
    """

    token = serializers.CharField(
        validators=[

        ]
    )

    def validate_token(self, data):
        """Verify token"""
        try:
            payload = jwt.decode(data, settings.SECRET_KEY, algorithms=['HS256'])
            if payload['type'] != 'email_confirmation':
                raise serializers.ValidationError('Invalid Token')
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError('Verification link has expired.')
        except jwt.PyJWTError:
            raise serializers.ValidationError('Invalid token')

    def save(self):
        """Update verified status for user"""
        payload = self.context['payload']
        user = User.objects.get(username=payload['user'])
        user.update(is_verified=True)
