"""
URL configuration for mathura_tourism project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tourism.custom_admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),
    path('api/', include('tourism.urls_api')),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('tourism.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
