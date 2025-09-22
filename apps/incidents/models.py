"""
Models for the incidents application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Client, User
from apps.alerts.models import Alert


class Incident(models.Model):
    """Model representing a security incident."""
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Nouveau'),
        ('assigned', 'Assigné'),
        ('in_progress', 'En cours'),
        ('on_hold', 'En attente'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    ]
    
    CATEGORY_CHOICES = [
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('ddos', 'DDoS'),
        ('data_breach', 'Fuite de données'),
        ('insider_threat', 'Menace interne'),
        ('vulnerability', 'Vulnérabilité'),
        ('policy_violation', 'Violation de politique'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='incidents')
    incident_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Related alerts
    related_alerts = models.ManyToManyField(Alert, related_name='incidents', blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents_by'
    )
    
    # Impact assessment
    impact_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    business_impact = models.TextField(blank=True)
    affected_systems = models.JSONField(default=list, blank=True)
    affected_users = models.PositiveIntegerField(default=0)
    
    # Timestamps
    detected_at = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    # Resolution
    resolution_summary = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    
    # Additional metadata
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-reported_at']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['client', 'priority']),
            models.Index(fields=['client', 'category']),
            models.Index(fields=['reported_at']),
            models.Index(fields=['impact_score']),
        ]
    
    def __str__(self):
        return f"{self.incident_id} - {self.title} ({self.get_priority_display()})"
    
    def get_priority_color(self):
        """Return color code for priority level."""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        return colors.get(self.priority, '#6c757d')
    
    def get_status_color(self):
        """Return color code for status."""
        colors = {
            'new': '#dc3545',
            'assigned': '#ffc107',
            'in_progress': '#17a2b8',
            'on_hold': '#6c757d',
            'resolved': '#28a745',
            'closed': '#6c757d',
        }
        return colors.get(self.status, '#6c757d')


class IncidentComment(models.Model):
    """Model for comments on incidents."""
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire d\'incident'
        verbose_name_plural = 'Commentaires d\'incidents'
    
    def __str__(self):
        return f"Commentaire sur {self.incident.incident_id} par {self.author.email}"


class IncidentAttachment(models.Model):
    """Model for file attachments on incidents."""
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='incident_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Pièce jointe d\'incident'
        verbose_name_plural = 'Pièces jointes d\'incidents'
    
    def __str__(self):
        return f"{self.filename} - {self.incident.incident_id}"


class IncidentTimeline(models.Model):
    """Model for tracking incident timeline events."""
    
    EVENT_TYPES = [
        ('created', 'Créé'),
        ('assigned', 'Assigné'),
        ('status_changed', 'Statut modifié'),
        ('comment_added', 'Commentaire ajouté'),
        ('attachment_added', 'Pièce jointe ajoutée'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
    ]
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='timeline')
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Événement de timeline'
        verbose_name_plural = 'Événements de timeline'
    
    def __str__(self):
        return f"{self.incident.incident_id} - {self.get_event_type_display()}"


class EscalationRule(models.Model):
    """Model for incident escalation rules."""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='escalation_rules')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Escalation criteria
    priority_levels = models.JSONField(default=list, blank=True)
    categories = models.JSONField(default=list, blank=True)
    min_impact_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    time_threshold_hours = models.PositiveIntegerField(default=24)
    
    # Escalation actions
    escalate_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escalation_rules'
    )
    notify_managers = models.BooleanField(default=False)
    auto_assign = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_escalation_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Règle d\'escalade'
        verbose_name_plural = 'Règles d\'escalade'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"
