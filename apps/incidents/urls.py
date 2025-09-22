from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'incidents', views.IncidentViewSet, basename='incident')
router.register(r'incidents/(?P<incident_pk>[^/.]+)/comments', views.IncidentCommentViewSet, basename='incident-comment')
router.register(r'incidents/(?P<incident_pk>[^/.]+)/attachments', views.IncidentAttachmentViewSet, basename='incident-attachment')
router.register(r'incidents/(?P<incident_pk>[^/.]+)/timeline', views.IncidentTimelineViewSet, basename='incident-timeline')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard_stats/', views.dashboard_stats_view, name='incident-dashboard-stats'),
]
