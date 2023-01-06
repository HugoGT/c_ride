"""Rides URLs module"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RideViewSet


router = DefaultRouter()
router.register(
    r'circles/(?P<slug_name>[a-zA-Z0-9_-]+)/rides',
    RideViewSet,
    basename='ride'
    )

urlpatterns = [
    path('', include(router.urls))
]
