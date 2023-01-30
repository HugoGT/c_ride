"""User Model"""


from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from cride.utils.models import CRideModel


class User(CRideModel, AbstractUser):
    """User Model

    Extend from Django's Abstract User, change the username field to email and some extra fields.
    """

    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )
    phone_regex = RegexValidator(
        regex=r'\+?1?\d{9,15}$',
        message='Phone number must be entered in the format: +987654321'
    )
    phone_number = models.CharField(
        'phone number',
        validators=[phone_regex],
        max_length=16,
        unique=True,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_client = models.BooleanField(
        'client status',
        default=True,
        help_text=(
            'Help easily distinguish users and perform queries.'
            'Clients are the main type of user.'
        )
    )

    is_verified = models.BooleanField(
        'verified',
        default=False,
        help_text="Set to true when the user have verified it's email address."
    )

    def __str__(self):
        return self.username
