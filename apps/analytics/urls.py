"""
URL configuration for analytics application.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()

urlpatterns = [
    # Risk scoring endpoints
    path('risk-scores/', views.RiskScoreListView.as_view(), name='risk-score-list'),
    path('metrics/', views.MetricListView.as_view(), name='metric-list'),
    path('dashboard-widgets/', views.DashboardWidgetListView.as_view(), name='dashboard-widget-list'),
    
    # Risk scoring actions
    path('calculate-risk-scores/', views.calculate_risk_scores, name='calculate-risk-scores'),
    path('risk-score-statistics/', views.risk_score_statistics, name='risk-score-statistics'),
    path('risk-score-distribution/', views.risk_score_distribution, name='risk-score-distribution'),
    
    # ML model management
    path('train-ml-models/', views.train_ml_models, name='train-ml-models'),
    
    # Threat intelligence
    path('threat-intelligence/<int:alert_id>/', views.threat_intelligence_enrichment, name='threat-intelligence-enrichment'),
    
    # Include router URLs
    path('', include(router.urls)),
]