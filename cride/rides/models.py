"""Rides models"""


from django.db import models

from cride.utils.models import CRideModel


class Ride(CRideModel):
    """Ride model"""

    offered_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    offered_in = models.ForeignKey('circles.Circle', on_delete=models.SET_NULL, null=True)

    passengers = models.ManyToManyField('users.User', related_name='passengers')

    available_seats = models.PositiveSmallIntegerField(default=1)
    comments = models.TextField(blank=True)

    departure_location = models.CharField(max_length=255)
    departure_date = models.DateTimeField()
    arrival_location = models.CharField(max_length=255)
    arrival_date = models.DateTimeField()

    rating = models.FloatField(null=True)

    is_active = models.BooleanField(
        'active status',
        default=True,
        help_text='Used for disabling the ride or marking it as finished.'
    )

    def __str__(self):
        """Return ride details."""
        return '{_from} to {to} | {day} {i_time} - {f_time}'.format(
            _from=self.departure_location,
            to=self.arrival_location,
            day=self.departure_date.strftime('%a %d, %b'),
            i_time=self.departure_date.strftime('%I:%M %p'),
            f_time=self.arrival_date.strftime('%I:%M %p'),
        )


class Rating(CRideModel):
    """Ride rating
    Rates are entities that store the rating a user gave to a ride, it ranges from 1 to 5 and it affects the ride offerer's overall reputation.
    """

    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='rated_ride'
    )
    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

    rating_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        help_text='User that emits the rating',
        related_name='rating_user',
    )
    rated_user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        help_text='User that receives the rating.',
        related_name='rated_user'
    )

    comments = models.TextField(blank=True)

    rating = models.IntegerField(default=1)

    def __str__(self):
        """Return summary."""
        return f'@{self.rating_user.username} rated {self.rating} @{self.rated_user.username}'
