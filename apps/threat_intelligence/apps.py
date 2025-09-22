"""
Apps configuration for threat_intelligence application.
"""
from django.apps import AppConfig


class ThreatIntelligenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.threat_intelligence'
    verbose_name = 'Threat Intelligence'
