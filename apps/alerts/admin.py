"""
Admin configuration for the alerts application.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Alert, AlertComment, AlertAttachment, AlertRule


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for Alert model."""
    
    list_display = [
        'alert_id', 'title', 'client', 'alert_type', 'severity', 'status',
        'risk_score', 'assigned_to', 'detected_at', 'created_at'
    ]
    list_filter = [
        'severity', 'status', 'alert_type', 'client', 'assigned_to',
        'detected_at', 'created_at'
    ]
    search_fields = [
        'alert_id', 'title', 'description', 'source_ip', 'destination_ip'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('alert_id', 'title', 'description', 'client')
        }),
        ('Classification', {
            'fields': ('alert_type', 'severity', 'status')
        }),
        ('Réseau', {
            'fields': ('source_ip', 'destination_ip', 'source_port', 'destination_port', 'protocol'),
            'classes': ('collapse',)
        }),
        ('Système source', {
            'fields': ('source_system', 'raw_data', 'tags'),
            'classes': ('collapse',)
        }),
        ('Assignation et score', {
            'fields': ('assigned_to', 'risk_score', 'risk_factors')
        }),
        ('Timestamps', {
            'fields': ('detected_at', 'created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('client', 'assigned_to')


@admin.register(AlertComment)
class AlertCommentAdmin(admin.ModelAdmin):
    """Admin configuration for AlertComment model."""
    
    list_display = ['alert', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at', 'author']
    search_fields = ['alert__alert_id', 'author__email', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Commentaire', {
            'fields': ('alert', 'author', 'content', 'is_internal')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AlertAttachment)
class AlertAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for AlertAttachment model."""
    
    list_display = ['alert', 'filename', 'file_size', 'mime_type', 'uploaded_by', 'uploaded_at']
    list_filter = ['mime_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['alert__alert_id', 'filename', 'uploaded_by__email']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Fichier', {
            'fields': ('alert', 'file', 'filename', 'file_size', 'mime_type')
        }),
        ('Upload', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """Admin configuration for AlertRule model."""
    
    list_display = [
        'name', 'client', 'is_active', 'alert_types_count', 'created_by', 'created_at'
    ]
    list_filter = ['is_active', 'client', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'client__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Règle', {
            'fields': ('name', 'description', 'client', 'is_active')
        }),
        ('Critères de filtrage', {
            'fields': ('alert_types', 'severity_levels', 'source_ips', 'destination_ips', 'keywords'),
            'classes': ('collapse',)
        }),
        ('Score de risque', {
            'fields': ('min_risk_score', 'max_risk_score'),
            'classes': ('collapse',)
        }),
        ('Notifications', {
            'fields': ('notify_email', 'notify_dashboard', 'email_recipients'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def alert_types_count(self, obj):
        """Display count of alert types."""
        return len(obj.alert_types) if obj.alert_types else 0
    alert_types_count.short_description = 'Types d\'alertes'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('client', 'created_by')
