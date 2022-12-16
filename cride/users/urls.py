"""Circles URLs module"""


from django.urls import path

from cride.users.views import (
    UserLoginAPIView,
    UserSignupAPIView,
    )


urlpatterns = [
    path('login', UserLoginAPIView.as_view(), name='login'),
    path('signup', UserSignupAPIView.as_view(), name='signup'),
]
