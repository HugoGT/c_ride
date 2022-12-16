"""Circles URLs module"""


from django.urls import path

from cride.users.views import (
    UserLoginAPIView,
    UserSignupAPIView,
    UserVerifyAPIView,
    )


urlpatterns = [
    path('signup', UserSignupAPIView.as_view(), name='signup'),
    path('verify', UserVerifyAPIView.as_view(), name='verify'),
    path('login', UserLoginAPIView.as_view(), name='login'),
]
