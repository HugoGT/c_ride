"""Main URLs module"""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),

    #Circles views
    path('', include(('cride.circles.urls', 'circles'), namespace='circles')),

    #Rides views
    path('', include(('cride.rides.urls', 'rides'), namespace='rides')),

    #Users views
    path('', include(('cride.users.urls', 'users'), namespace='users')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
