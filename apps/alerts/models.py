"""
Models for the alerts application.
"""
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Client, User


class Alert(models.Model):
    """Model representing a security alert."""
    
    SEVERITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('closed', 'Fermé'),
        ('false_positive', 'Faux positif'),
    ]
    
    TYPE_CHOICES = [
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('ddos', 'DDoS'),
        ('intrusion', 'Intrusion'),
        ('data_exfiltration', 'Exfiltration de données'),
        ('privilege_escalation', 'Élévation de privilèges'),
        ('suspicious_activity', 'Activité suspecte'),
        ('vulnerability', 'Vulnérabilité'),
        ('policy_violation', 'Violation de politique'),
        ('other', 'Autre'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='alerts')
    alert_id = models.CharField(max_length=100, unique=True)  # External alert ID
    title = models.CharField(max_length=200)
    description = models.TextField()
    alert_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Network information
    source_ip = models.GenericIPAddressField(blank=True, null=True)
    destination_ip = models.GenericIPAddressField(blank=True, null=True)
    source_port = models.PositiveIntegerField(blank=True, null=True)
    destination_port = models.PositiveIntegerField(blank=True, null=True)
    protocol = models.CharField(max_length=20, blank=True)
    
    # Additional metadata
    source_system = models.CharField(max_length=100, blank=True)  # SIEM, Firewall, etc.
    raw_data = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    detected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    
    # Risk scoring
    risk_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    risk_factors = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'
        indexes = [
            models.Index(fields=['client', 'severity']),
            models.Index(fields=['client', 'status']),
            models.Index(fields=['client', 'alert_type']),
            models.Index(fields=['detected_at']),
            models.Index(fields=['risk_score']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.title} ({self.get_severity_display()})"
    
    def get_severity_color(self):
        """Return color code for severity level."""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'critical': '#dc3545',
        }
        return colors.get(self.severity, '#6c757d')
    
    def get_status_color(self):
        """Return color code for status."""
        colors = {
            'open': '#dc3545',
            'in_progress': '#ffc107',
            'closed': '#28a745',
            'false_positive': '#6c757d',
        }
        return colors.get(self.status, '#6c757d')
    
    def get_resolution_time(self):
        """Calculate resolution time in minutes."""
        if self.status == 'closed' and self.closed_at:
            delta = self.closed_at - self.detected_at
            return int(delta.total_seconds() / 60)
        return None


class AlertComment(models.Model):
    """Model for comments on alerts."""
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_internal = models.BooleanField(default=False)  # Internal SOC comments
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire d\'alerte'
        verbose_name_plural = 'Commentaires d\'alertes'
    
    def __str__(self):
        return f"Commentaire sur {self.alert.alert_id} par {self.author.email}"


class AlertAttachment(models.Model):
    """Model for file attachments on alerts."""
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='alert_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Pièce jointe d\'alerte'
        verbose_name_plural = 'Pièces jointes d\'alertes'
    
    def __str__(self):
        return f"{self.filename} - {self.alert.alert_id}"


class AlertRule(models.Model):
    """Model for custom alert rules and filters."""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='alert_rules')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # Filter criteria
    alert_types = models.JSONField(default=list, blank=True)
    severity_levels = models.JSONField(default=list, blank=True)
    source_ips = models.JSONField(default=list, blank=True)
    destination_ips = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    min_risk_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    max_risk_score = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    
    # Notification settings
    notify_email = models.BooleanField(default=True)
    notify_dashboard = models.BooleanField(default=True)
    email_recipients = models.JSONField(default=list, blank=True)
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Règle d\'alerte'
        verbose_name_plural = 'Règles d\'alertes'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


# Signals for automatic processing
@receiver(post_save, sender=Alert)
def alert_created_handler(sender, instance, created, **kwargs):
    """Handle alert creation - trigger automatic processing."""
    if created:
        # Import here to avoid circular imports
        from apps.analytics.services import RiskScoringService
        from apps.integrations.streaming import alert_streaming_service
        
        # Calculate risk score immediately (synchronous)
        try:
            scoring_service = RiskScoringService()
            score, factors = scoring_service.calculate_alert_risk_score(instance)
            
            # Update alert with calculated score
            instance.risk_score = score
            instance.risk_factors = factors
            instance.save(update_fields=['risk_score', 'risk_factors'])
            
            print(f"Alert {instance.alert_id} created with risk score {score:.2f} for client {instance.client.name}")
            
            # Publish alert via WebSocket for real-time updates (optional)
            try:
                from apps.integrations.streaming import alert_streaming_service
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(alert_streaming_service.publish_alert(instance))
                loop.close()
            except ImportError:
                print("WebSocket not available (channels not installed)")
            except Exception as ws_error:
                print(f"Error publishing alert via WebSocket: {str(ws_error)}")
            
        except Exception as e:
            print(f"Error calculating risk score for alert {instance.alert_id}: {str(e)}")
            # Set default score if calculation fails
            instance.risk_score = 5.0
            instance.risk_factors = {'error': str(e), 'methodology': 'default_fallback'}
            instance.save(update_fields=['risk_score', 'risk_factors'])
