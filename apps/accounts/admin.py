"""
Admin configuration for the accounts application.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Client, UserSession, AuditLog


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin configuration for Client model."""
    
    list_display = ['name', 'contact_email', 'contact_phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_email', 'contact_phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'contact_email', 'contact_phone', 'address')
        }),
        ('Configuration', {
            'fields': ('timezone', 'notification_preferences', 'custom_settings')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = ['email', 'get_full_name', 'role', 'client', 'is_active', 'mfa_enrolled', 'created_at']
    list_filter = ['role', 'is_active', 'mfa_enrolled', 'is_verified', 'client', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('username', 'email', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'phone', 'avatar')
        }),
        ('Rôle et organisation', {
            'fields': ('role', 'client')
        }),
        ('Sécurité', {
            'fields': ('mfa_enrolled', 'mfa_secret', 'is_verified', 'last_login_ip')
        }),
        ('Préférences', {
            'fields': ('preferences', 'notification_settings'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Informations de connexion', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Informations personnelles', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone'),
        }),
        ('Rôle et organisation', {
            'classes': ('wide',),
            'fields': ('role', 'client'),
        }),
    )
    
    def get_full_name(self, obj):
        """Display full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Nom complet'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model."""
    
    list_display = ['user', 'ip_address', 'is_active', 'created_at', 'last_activity']
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address', 'session_key']
    readonly_fields = ['created_at', 'last_activity']
    
    fieldsets = (
        ('Session', {
            'fields': ('user', 'session_key', 'is_active')
        }),
        ('Informations de connexion', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_activity')
        }),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""
    
    list_display = ['user', 'action', 'resource_type', 'resource_id', 'ip_address', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at', 'user']
    search_fields = ['user__email', 'description', 'ip_address', 'resource_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Action', {
            'fields': ('user', 'action', 'resource_type', 'resource_id', 'description')
        }),
        ('Contexte', {
            'fields': ('ip_address', 'user_agent', 'metadata')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding audit logs manually."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs."""
        return False
