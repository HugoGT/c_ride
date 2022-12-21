"""Circles URLs module"""


from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CircleViewSet


router = DefaultRouter()
router.register(r'circles', CircleViewSet, basename='circle')

urlpatterns = [
    path('', include(router.urls))
]
