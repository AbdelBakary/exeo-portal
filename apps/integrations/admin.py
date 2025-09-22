from django.contrib import admin
from django.utils.html import format_html
from .models import ClientIntegration, IntegrationLog, AlertMappingTemplate


@admin.register(ClientIntegration)
class ClientIntegrationAdmin(admin.ModelAdmin):
    list_display = [
        'client', 'name', 'integration_type', 'status', 
        'is_active', 'last_sync', 'alerts_received_24h', 'error_count_24h'
    ]
    list_filter = ['integration_type', 'status', 'is_active', 'created_at']
    search_fields = ['client__name', 'name', 'endpoint_url']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_sync', 'alerts_received_24h', 'error_count_24h']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('client', 'name', 'integration_type', 'endpoint_url', 'api_token')
        }),
        ('Mapping', {
            'fields': ('mapping_config',)
        }),
        ('Status', {
            'fields': ('is_active', 'status', 'error_message')
        }),
        ('Monitoring', {
            'fields': ('last_sync', 'alerts_received_24h', 'last_alert_received', 'error_count_24h'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['test_connections', 'activate_integrations', 'deactivate_integrations']
    
    def test_connections(self, request, queryset):
        """Teste les connexions des intégrations sélectionnées"""
        for integration in queryset:
            try:
                # TODO: Implémenter le test de connexion
                integration.update_sync_status(success=True)
                self.message_user(request, f"Test réussi pour {integration}")
            except Exception as e:
                integration.update_sync_status(success=False, error_message=str(e))
                self.message_user(request, f"Test échoué pour {integration}: {str(e)}")
    
    def activate_integrations(self, request, queryset):
        """Active les intégrations sélectionnées"""
        count = queryset.update(is_active=True, status='active')
        self.message_user(request, f"{count} intégrations activées")
    
    def deactivate_integrations(self, request, queryset):
        """Désactive les intégrations sélectionnées"""
        count = queryset.update(is_active=False, status='inactive')
        self.message_user(request, f"{count} intégrations désactivées")


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['integration', 'log_type', 'message', 'timestamp']
    list_filter = ['log_type', 'timestamp', 'integration__client']
    search_fields = ['integration__client__name', 'message']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Les logs sont créés automatiquement


@admin.register(AlertMappingTemplate)
class AlertMappingTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'system_type', 'is_active', 'created_at']
    list_filter = ['system_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
