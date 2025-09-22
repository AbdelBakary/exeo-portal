"""
Apps configuration for soar application.
"""
from django.apps import AppConfig


class SoarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.soar'
    verbose_name = 'SOAR (Automatisation)'
