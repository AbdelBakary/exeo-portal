from django.db import models
from django.utils import timezone
from apps.accounts.models import Client
import uuid


class ClientIntegration(models.Model):
    """Configuration d'intégration pour chaque client"""
    
    INTEGRATION_TYPES = [
        ('webhook', 'Webhook'),
        ('siem', 'SIEM'),
        ('firewall', 'Firewall'),
        ('edr', 'EDR/XDR'),
        ('cloud', 'Cloud Security'),
        ('api', 'API REST'),
        ('syslog', 'Syslog'),
    ]
    
    STATUS_CHOICES = [
        ('inactive', 'Inactive'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('testing', 'Testing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='integrations')
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    name = models.CharField(max_length=100, help_text="Nom de l'intégration")
    endpoint_url = models.URLField(blank=True, null=True, help_text="URL du système client")
    api_token = models.CharField(max_length=255, blank=True, null=True, help_text="Token d'authentification")
    mapping_config = models.JSONField(default=dict, help_text="Configuration de mapping des champs")
    is_active = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Métadonnées de monitoring
    alerts_received_24h = models.IntegerField(default=0)
    last_alert_received = models.DateTimeField(null=True, blank=True)
    error_count_24h = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['client', 'name']
    
    def __str__(self):
        return f"{self.client.name} - {self.name} ({self.integration_type})"
    
    def update_sync_status(self, success=True, error_message=None):
        """Met à jour le statut de synchronisation"""
        self.last_sync = timezone.now()
        if success:
            self.status = 'active'
            self.error_message = None
        else:
            self.status = 'error'
            self.error_message = error_message
        self.save(update_fields=['last_sync', 'status', 'error_message'])
    
    def increment_alert_count(self):
        """Incrémente le compteur d'alertes reçues"""
        self.alerts_received_24h += 1
        self.last_alert_received = timezone.now()
        self.save(update_fields=['alerts_received_24h', 'last_alert_received'])
    
    def increment_error_count(self):
        """Incrémente le compteur d'erreurs"""
        self.error_count_24h += 1
        self.save(update_fields=['error_count_24h'])


class IntegrationLog(models.Model):
    """Logs des intégrations pour monitoring et debugging"""
    
    LOG_TYPES = [
        ('alert_received', 'Alert Received'),
        ('alert_processed', 'Alert Processed'),
        ('error', 'Error'),
        ('connection_test', 'Connection Test'),
        ('sync_started', 'Sync Started'),
        ('sync_completed', 'Sync Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(ClientIntegration, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.integration} - {self.log_type} - {self.timestamp}"


class AlertMappingTemplate(models.Model):
    """Templates de mapping pour différents types de systèmes"""
    
    SYSTEM_TYPES = [
        ('splunk', 'Splunk'),
        ('qradar', 'QRadar'),
        ('arcsight', 'ArcSight'),
        ('fortinet', 'Fortinet'),
        ('paloalto', 'Palo Alto'),
        ('cisco', 'Cisco'),
        ('crowdstrike', 'CrowdStrike'),
        ('sentinelone', 'SentinelOne'),
        ('microsoft_defender', 'Microsoft Defender'),
        ('aws_guardduty', 'AWS GuardDuty'),
        ('azure_security', 'Azure Security Center'),
        ('gcp_security', 'GCP Security Command Center'),
    ]
    
    name = models.CharField(max_length=100)
    system_type = models.CharField(max_length=50, choices=SYSTEM_TYPES)
    mapping_config = models.JSONField(help_text="Configuration de mapping par défaut")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.system_type})"
