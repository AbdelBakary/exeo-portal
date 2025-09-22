"""
URL configuration for the alerts application.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Alerts
    path('', views.AlertListCreateView.as_view(), name='alert_list_create'),
    path('<int:pk>/', views.AlertDetailView.as_view(), name='alert_detail'),
    path('<int:pk>/assign/', views.assign_alert, name='assign_alert'),
    path('statistics/', views.alert_statistics, name='alert_statistics'),
    path('bulk-update/', views.bulk_update_alerts, name='bulk_update_alerts'),
    
    # Alert comments
    path('<int:alert_id>/comments/', views.AlertCommentListCreateView.as_view(), name='alert_comment_list_create'),
    
    # Alert attachments
    path('<int:alert_id>/attachments/', views.AlertAttachmentListCreateView.as_view(), name='alert_attachment_list_create'),
    
    # Alert rules
    path('rules/', views.AlertRuleListCreateView.as_view(), name='alert_rule_list_create'),
    path('rules/<int:pk>/', views.AlertRuleDetailView.as_view(), name='alert_rule_detail'),
]
