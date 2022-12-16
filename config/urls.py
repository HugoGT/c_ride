"""Main URLs module"""

from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    #Users views
    path('', include(('cride.users.urls', 'users'), namespace='users')),

    #Circles views
    path('', include(('cride.circles.urls', 'circles'), namespace='circles')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
