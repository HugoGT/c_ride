"""Cricles Admin"""


from django.contrib import admin

from cride.circles.models import Circle


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
