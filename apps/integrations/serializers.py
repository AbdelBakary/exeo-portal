from rest_framework import serializers
from .models import ClientIntegration, IntegrationLog, AlertMappingTemplate


class ClientIntegrationSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)
    last_sync_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientIntegration
        fields = [
            'id', 'client', 'client_name', 'integration_type', 'name',
            'endpoint_url', 'api_token', 'mapping_config', 'is_active',
            'last_sync', 'last_sync_formatted', 'status', 'error_message',
            'alerts_received_24h', 'last_alert_received', 'error_count_24h',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync', 'alerts_received_24h', 'error_count_24h']
    
    def get_last_sync_formatted(self, obj):
        if obj.last_sync:
            return obj.last_sync.strftime('%Y-%m-%d %H:%M:%S')
        return None


class IntegrationLogSerializer(serializers.ModelSerializer):
    integration_name = serializers.CharField(source='integration.name', read_only=True)
    client_name = serializers.CharField(source='integration.client.name', read_only=True)
    
    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'integration_name', 'client_name',
            'log_type', 'message', 'details', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']


class AlertMappingTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertMappingTemplate
        fields = [
            'id', 'name', 'system_type', 'mapping_config',
            'description', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WebhookAlertSerializer(serializers.Serializer):
    """Serializer pour les alertes reçues via webhook"""
    external_id = serializers.CharField(help_text="ID de l'alerte dans le système client")
    title = serializers.CharField(help_text="Titre de l'alerte")
    description = serializers.CharField(required=False, allow_blank=True)
    severity = serializers.ChoiceField(choices=['low', 'medium', 'high', 'critical'])
    alert_type = serializers.CharField(help_text="Type d'alerte (intrusion, malware, etc.)")
    source_ip = serializers.IPAddressField(required=False, allow_blank=True)
    destination_ip = serializers.IPAddressField(required=False, allow_blank=True)
    source_port = serializers.IntegerField(required=False, allow_null=True)
    destination_port = serializers.IntegerField(required=False, allow_null=True)
    protocol = serializers.CharField(required=False, allow_blank=True)
    source_system = serializers.CharField(required=False, allow_blank=True)
    timestamp = serializers.DateTimeField(help_text="Timestamp de détection")
    raw_data = serializers.JSONField(required=False, default=dict)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    
    def validate_severity(self, value):
        """Normalise la sévérité"""
        severity_mapping = {
            '1': 'critical', '2': 'high', '3': 'medium', '4': 'low',
            'critical': 'critical', 'high': 'high', 'medium': 'medium', 'low': 'low',
            'info': 'low', 'warning': 'medium', 'error': 'high', 'fatal': 'critical'
        }
        return severity_mapping.get(str(value).lower(), value.lower())
