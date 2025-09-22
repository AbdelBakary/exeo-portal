from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, webhooks

# Router pour les vues basées sur les ViewSets
router = DefaultRouter()
router.register(r'integrations', views.ClientIntegrationListCreateView, basename='integration')

urlpatterns = [
    # Webhooks (pas d'authentification requise)
    path('webhook/', webhooks.client_webhook, name='client_webhook'),
    path('webhook/status/', webhooks.webhook_status, name='webhook_status'),
    path('webhook/test/', webhooks.test_webhook, name='test_webhook'),
    
    # Intégrations (authentification requise)
    path('integrations/', views.ClientIntegrationListCreateView.as_view(), name='integration-list'),
    path('integrations/<uuid:pk>/', views.ClientIntegrationDetailView.as_view(), name='integration-detail'),
    path('integrations/<uuid:integration_id>/test/', views.test_integration_connection, name='test-integration'),
    path('integrations/<uuid:integration_id>/sync/', views.sync_integration_alerts, name='sync-integration'),
    
    # Logs
    path('logs/', views.IntegrationLogListView.as_view(), name='integration-logs'),
    
    # Templates de mapping
    path('mapping-templates/', views.AlertMappingTemplateListView.as_view(), name='mapping-templates'),
    
    # Statistiques
    path('statistics/', views.integration_statistics, name='integration-statistics'),
]
