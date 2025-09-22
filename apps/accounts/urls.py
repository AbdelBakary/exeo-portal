"""
URL configuration for the accounts application.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change_password'),
    
    # User management
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Client management
    path('clients/', views.ClientListCreateView.as_view(), name='client_list_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    
    # Sessions and audit
    path('sessions/', views.UserSessionListView.as_view(), name='user_session_list'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
]
