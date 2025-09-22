"""
Models for the reports application.
"""
from django.db import models
from apps.accounts.models import Client, User


class Report(models.Model):
    """Model for security reports."""
    
    REPORT_TYPES = [
        ('security_dashboard', 'Tableau de bord de sécurité'),
        ('incident_summary', 'Résumé d\'incidents'),
        ('threat_intelligence', 'Threat Intelligence'),
        ('compliance', 'Conformité'),
        ('executive', 'Rapport exécutif'),
        ('technical', 'Rapport technique'),
        ('custom', 'Personnalisé'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('generating', 'Génération en cours'),
        ('ready', 'Prêt'),
        ('sent', 'Envoyé'),
        ('archived', 'Archivé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reports')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Report content
    content = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    
    # Configuration
    template_config = models.JSONField(default=dict, blank=True)
    data_filters = models.JSONField(default=dict, blank=True)
    output_format = models.CharField(max_length=20, default='pdf')
    
    # File information
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    is_public = models.BooleanField(default=False)
    
    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    generated_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
    
    def __str__(self):
        return f"{self.title} - {self.client.name}"


class ReportSchedule(models.Model):
    """Model for scheduled report generation."""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    
    DAY_CHOICES = [
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='report_schedules')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Schedule configuration
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    day_of_week = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    day_of_month = models.PositiveIntegerField(blank=True, null=True)
    time = models.TimeField()
    
    # Report template
    report_template = models.ForeignKey(
        'analytics.ReportTemplate',
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    
    # Recipients
    email_recipients = models.JSONField(default=list, blank=True)
    include_attachments = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(blank=True, null=True)
    next_run = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Planification de rapport'
        verbose_name_plural = 'Planifications de rapport'
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


class ReportDelivery(models.Model):
    """Model for tracking report deliveries."""
    
    DELIVERY_STATUS = [
        ('pending', 'En attente'),
        ('sent', 'Envoyé'),
        ('delivered', 'Livré'),
        ('failed', 'Échoué'),
        ('bounced', 'Rejeté'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='deliveries')
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200, blank=True)
    
    # Delivery details
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending')
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Tracking
    tracking_id = models.CharField(max_length=100, blank=True)
    open_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Livraison de rapport'
        verbose_name_plural = 'Livraisons de rapport'
    
    def __str__(self):
        return f"{self.report.title} - {self.recipient_email}"


class ReportAccess(models.Model):
    """Model for tracking report access and permissions."""
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_access')
    
    # Access details
    access_type = models.CharField(max_length=20, default='view')  # view, download, share
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    accessed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-accessed_at']
        verbose_name = 'Accès au rapport'
        verbose_name_plural = 'Accès aux rapports'
    
    def __str__(self):
        return f"{self.user.email} - {self.report.title} - {self.accessed_at}"
