"""Cricles Admin"""


import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import now, timedelta, localtime, datetime

from cride.circles.models import Circle
from cride.rides.models import Ride


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Cricle admin"""

    list_display = (
        'slug_name',
        'name',
        'verified',
        'is_public',
        'is_limited',
        'members_limit',
    )
    search_fields = ('slug_name', 'name')
    list_filter = (
        'is_public',
        'verified',
        'is_limited',
    )
    actions = ['make_verified', 'make_unverified']

    def make_verified(self, request, queryset):
        """Make circles verified"""
        queryset.update(verified=True)

    make_verified.short_description = 'Make selected circles verified'

    def make_unverified(self, request, queryset):
        """Make circles verified"""
        queryset.update(verified=False)

    make_unverified.short_description = 'Make selected circles unverified'

    def download_todays_rides(self, request, queryset):
        """Return today's rides"""
        time = localtime(now())
        start = localtime(datetime(time.year, time.month, time.day, 0, 0, 0))
        end = start + timedelta(days=1)
        rides = Ride.objects.filter(
            offered_in__in=queryset.values_list('id'),
            departure_date__gte=start,
            departure_date__lte=end,
        ).order_by('departure_date')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="todaysrides.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'id',
            'passengers',
            'departure_location',
            'departure_date',
            'arrival_location',
            'arrival_date,',
            'rating'
        ])
        for ride in rides:
            writer.writerow([
                ride.pk,
                rides.passengers.count(),
                ride.departure_location,
                str(ride.departure_date),
                ride.arrival_location,
                str(ride.arrival_date),
                ride.rating
            ])

        return response

    download_todays_rides.short_description = "Download todays rides"
