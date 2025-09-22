"""
URL configuration for exeo_portal project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('', lambda request: HttpResponse('EXEO Security Portal API - Backend is running!', status=200)),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/alerts/', include('apps.alerts.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/threat-intelligence/', include('apps.threat_intelligence.urls')),
    path('api/soar/', include('apps.soar.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
    path('health/', lambda request: HttpResponse('OK', status=200)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
