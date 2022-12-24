"""Circles URLs module"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CircleViewSet, MembershipViewSet


router = DefaultRouter()
router.register(r'circles', CircleViewSet, basename='circle')
router.register(
    r'circles/(?P<slug_name>[a-zA-Z0-9_-]+)/members',
    MembershipViewSet, basename='membership'
    )

urlpatterns = [
    path('', include(router.urls))
]
