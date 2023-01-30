"""Rides Admin"""


from django.contrib import admin

from cride.rides.models import Ride


@admin.register(Ride)
class CircleAdmin(admin.ModelAdmin):
    """Cricle admin"""

    list_display = (
        'offered_by',
        'offered_in',
        'passengers',
        'departure_location',
        'arrival_location'
    )
    search_fields = ('slug_name', 'name')
    list_filter = (
        'offered_by',
        'offered_in',
        'passengers'
    )
