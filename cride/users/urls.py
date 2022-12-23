"""Circles URLs module"""


from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, AuthViewSet


router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
