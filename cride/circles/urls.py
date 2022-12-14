"""Circles URLs module"""


from django.urls import path

from cride.circles.views import list_circles
from cride.circles.views import create_circle


urlpatterns = [
    path('circles/', list_circles),
    path('circles/create/', create_circle),
]
