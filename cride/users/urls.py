"""Circles URLs module"""


from django.urls import path

from cride.users.views import UserLoginAPIView


urlpatterns = [
    path('login', UserLoginAPIView.as_view(), name='login'),
]
