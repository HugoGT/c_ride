"""Celery tasks"""


import jwt

from celery.decorators import task, periodic_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta

from cride.rides.models import Ride
from cride.users.models import User


def gen_verification_token(user):
    """Create JSON Web Token that the user can use to verify its account"""
    exp_date = now() + timedelta(days=2)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token


@task(name='send_confirmation_email', max_retries=3)
def send_confirmation_email(user_pk):
    """Sends a link to verify users account"""
    user = User.objects.get(pk=user_pk)
    verification_token = gen_verification_token(user)
    subject = f'Welcome @{user.username}! Verify your account to start using Comparte Ride'
    from_email = 'Comparte Ride <noreply@comparteride.com>'
    content = render_to_string(
        'emails/users/account_verification.html',
        {'token': verification_token, 'user': user}
    )
    msg = EmailMultiAlternatives(subject, content, from_email, [user.email])
    msg.attach_alternative(content, "text/html")
    msg.send()


@periodic_task(name='disable_finished_rides', run_every=timedelta(minutes=30))
def disable_finished_rides():
    """Disable finished rides"""
    time = now()
    offset = time + timedelta(seconds=5)

    # Updates finished rides
    rides = Ride.objects.filter(
        arrival_date__gte=now,
        arrival_date__lte=offset,
        is_active=True
    )
    rides.update(is_active=False)
