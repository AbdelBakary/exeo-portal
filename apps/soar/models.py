"""
Models for the SOAR (Security Orchestration, Automation and Response) application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Client, User
from apps.alerts.models import Alert
from apps.incidents.models import Incident


class Playbook(models.Model):
    """Model representing a SOAR playbook."""
    
    TRIGGER_TYPES = [
        ('alert_created', 'Alerte créée'),
        ('alert_updated', 'Alerte mise à jour'),
        ('incident_created', 'Incident créé'),
        ('incident_updated', 'Incident mis à jour'),
        ('risk_score_threshold', 'Seuil de score de risque'),
        ('time_based', 'Basé sur le temps'),
        ('manual', 'Manuel'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('paused', 'En pause'),
        ('archived', 'Archivé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='playbooks')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Trigger configuration
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    trigger_conditions = models.JSONField(default=dict, blank=True)
    
    # Playbook definition
    steps = models.JSONField(default=list, blank=True)  # List of action steps
    variables = models.JSONField(default=dict, blank=True)  # Playbook variables
    
    # Execution settings
    is_enabled = models.BooleanField(default=True)
    max_execution_time = models.PositiveIntegerField(default=3600)  # seconds
    retry_count = models.PositiveIntegerField(default=3)
    retry_delay = models.PositiveIntegerField(default=60)  # seconds
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_playbooks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_executed = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Playbook SOAR'
        verbose_name_plural = 'Playbooks SOAR'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


class PlaybookExecution(models.Model):
    """Model representing a playbook execution instance."""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('timeout', 'Timeout'),
    ]
    
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='executions')
    trigger_type = models.CharField(max_length=50)
    trigger_data = models.JSONField(default=dict, blank=True)
    
    # Execution details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    execution_time = models.PositiveIntegerField(blank=True, null=True)  # seconds
    
    # Results
    steps_completed = models.PositiveIntegerField(default=0)
    total_steps = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    
    # Output
    output = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    logs = models.TextField(blank=True)
    
    # Context
    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='playbook_executions'
    )
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Exécution de playbook'
        verbose_name_plural = 'Exécutions de playbook'
    
    def __str__(self):
        return f"{self.playbook.name} - {self.get_status_display()}"


class Action(models.Model):
    """Model representing a SOAR action."""
    
    ACTION_TYPES = [
        ('email_notification', 'Notification email'),
        ('slack_notification', 'Notification Slack'),
        ('create_ticket', 'Créer un ticket'),
        ('assign_alert', 'Assigner une alerte'),
        ('block_ip', 'Bloquer une IP'),
        ('quarantine_file', 'Mettre en quarantaine un fichier'),
        ('update_status', 'Mettre à jour le statut'),
        ('add_comment', 'Ajouter un commentaire'),
        ('escalate', 'Escalader'),
        ('webhook', 'Webhook'),
        ('script', 'Script personnalisé'),
    ]
    
    name = models.CharField(max_length=200)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    
    # Action configuration
    parameters = models.JSONField(default=dict, blank=True)
    conditions = models.JSONField(default=dict, blank=True)
    
    # Integration settings
    integration_config = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_actions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Action SOAR'
        verbose_name_plural = 'Actions SOAR'
    
    def __str__(self):
        return f"{self.name} ({self.get_action_type_display()})"


class Integration(models.Model):
    """Model representing external system integrations."""
    
    INTEGRATION_TYPES = [
        ('firewall', 'Pare-feu'),
        ('siem', 'SIEM'),
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('webhook', 'Webhook'),
        ('api', 'API REST'),
        ('ldap', 'LDAP/Active Directory'),
        ('ticketing', 'Système de tickets'),
        ('other', 'Autre'),
    ]
    
    name = models.CharField(max_length=200)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPES)
    description = models.TextField(blank=True)
    
    # Configuration
    base_url = models.URLField(blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=500, blank=True)
    additional_config = models.JSONField(default=dict, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_healthy = models.BooleanField(default=True)
    last_test = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_integrations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Intégration'
        verbose_name_plural = 'Intégrations'
    
    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"


class AutomationRule(models.Model):
    """Model for automation rules that trigger playbooks."""
    
    RULE_TYPES = [
        ('alert_risk_score', 'Score de risque d\'alerte'),
        ('alert_severity', 'Sévérité d\'alerte'),
        ('alert_type', 'Type d\'alerte'),
        ('incident_priority', 'Priorité d\'incident'),
        ('time_based', 'Basé sur le temps'),
        ('custom', 'Personnalisé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='automation_rules')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPES)
    
    # Rule conditions
    conditions = models.JSONField(default=dict, blank=True)
    is_enabled = models.BooleanField(default=True)
    
    # Actions
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE, related_name='automation_rules')
    execution_delay = models.PositiveIntegerField(default=0)  # seconds
    
    # Statistics
    trigger_count = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    failure_count = models.PositiveIntegerField(default=0)
    last_triggered = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_automation_rules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Règle d\'automatisation'
        verbose_name_plural = 'Règles d\'automatisation'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


class SOARLog(models.Model):
    """Model for logging SOAR activities."""
    
    LOG_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
        ('critical', 'Critique'),
    ]
    
    level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    component = models.CharField(max_length=100)  # playbook, action, integration, etc.
    execution = models.ForeignKey(
        PlaybookExecution,
        on_delete=models.CASCADE,
        related_name='soar_logs',
        null=True,
        blank=True
    )
    
    # Context
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='soar_logs')
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='soar_logs'
    )
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Log SOAR'
        verbose_name_plural = 'Logs SOAR'
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.component} - {self.created_at}"
