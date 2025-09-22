"""
Models for the analytics application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Client, User


class RiskScore(models.Model):
    """Model for storing calculated risk scores."""
    
    SCORE_TYPES = [
        ('alert', 'Alerte'),
        ('incident', 'Incident'),
        ('client', 'Client'),
        ('asset', 'Asset'),
        ('overall', 'Global'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='risk_scores')
    score_type = models.CharField(max_length=20, choices=SCORE_TYPES)
    entity_id = models.CharField(max_length=100)  # ID of the scored entity
    entity_type = models.CharField(max_length=50)  # Type of the scored entity
    
    # Score details
    score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    confidence = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Scoring factors
    factors = models.JSONField(default=dict, blank=True)
    methodology = models.CharField(max_length=100, default='ml_model_v1')
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now_add=True)
    calculated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calculated_risk_scores'
    )
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Score de risque'
        verbose_name_plural = 'Scores de risque'
        indexes = [
            models.Index(fields=['client', 'score_type']),
            models.Index(fields=['entity_id', 'entity_type']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.client.name} - {self.get_score_type_display()}: {self.score}"


class DashboardWidget(models.Model):
    """Model for dashboard widgets configuration."""
    
    WIDGET_TYPES = [
        ('chart', 'Graphique'),
        ('table', 'Tableau'),
        ('metric', 'Métrique'),
        ('alert', 'Alerte'),
        ('map', 'Carte'),
        ('timeline', 'Timeline'),
    ]
    
    CHART_TYPES = [
        ('line', 'Ligne'),
        ('bar', 'Barres'),
        ('pie', 'Camembert'),
        ('doughnut', 'Donut'),
        ('area', 'Aire'),
        ('scatter', 'Dispersion'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='dashboard_widgets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True)
    
    # Configuration
    config = models.JSONField(default=dict, blank=True)
    data_source = models.CharField(max_length=100)  # API endpoint or data source
    refresh_interval = models.PositiveIntegerField(default=300)  # seconds
    
    # Display settings
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    width = models.PositiveIntegerField(default=4)
    height = models.PositiveIntegerField(default=3)
    is_visible = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_widgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
        verbose_name = 'Widget de tableau de bord'
        verbose_name_plural = 'Widgets de tableau de bord'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


class AnalyticsEvent(models.Model):
    """Model for tracking analytics events."""
    
    EVENT_TYPES = [
        ('page_view', 'Vue de page'),
        ('widget_interaction', 'Interaction avec widget'),
        ('filter_applied', 'Filtre appliqué'),
        ('export_performed', 'Export effectué'),
        ('search_performed', 'Recherche effectuée'),
        ('alert_clicked', 'Alerte cliquée'),
        ('incident_clicked', 'Incident cliqué'),
        ('report_generated', 'Rapport généré'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='analytics_events')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_events')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    
    # Event details
    page_url = models.URLField(blank=True)
    component = models.CharField(max_length=100, blank=True)
    action = models.CharField(max_length=100, blank=True)
    
    # Event data
    properties = models.JSONField(default=dict, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Événement analytique'
        verbose_name_plural = 'Événements analytiques'
        indexes = [
            models.Index(fields=['client', 'event_type']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_event_type_display()} - {self.created_at}"


class ReportTemplate(models.Model):
    """Model for report templates."""
    
    REPORT_TYPES = [
        ('security_summary', 'Résumé de sécurité'),
        ('incident_report', 'Rapport d\'incident'),
        ('threat_analysis', 'Analyse de menaces'),
        ('compliance', 'Conformité'),
        ('executive', 'Exécutif'),
        ('technical', 'Technique'),
        ('custom', 'Personnalisé'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    
    # Template configuration
    template_config = models.JSONField(default=dict, blank=True)
    data_sources = models.JSONField(default=list, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Output settings
    output_format = models.CharField(max_length=20, default='pdf')  # pdf, excel, csv, html
    schedule = models.CharField(max_length=100, blank=True)  # Cron expression
    is_scheduled = models.BooleanField(default=False)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Modèle de rapport'
        verbose_name_plural = 'Modèles de rapport'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


class GeneratedReport(models.Model):
    """Model for generated reports."""
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('generating', 'Génération en cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='generated_reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_reports')
    
    # Report details
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File information
    file_path = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    file_format = models.CharField(max_length=20, default='pdf')
    
    # Generation details
    parameters = models.JSONField(default=dict, blank=True)
    data_range_start = models.DateTimeField(blank=True, null=True)
    data_range_end = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Rapport généré'
        verbose_name_plural = 'Rapports générés'
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Metric(models.Model):
    """Model for storing calculated metrics."""
    
    METRIC_TYPES = [
        ('count', 'Compteur'),
        ('sum', 'Somme'),
        ('average', 'Moyenne'),
        ('percentage', 'Pourcentage'),
        ('rate', 'Taux'),
        ('trend', 'Tendance'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    
    # Metric value
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    
    # Time period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Additional data
    dimensions = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Calculation details
    calculation_method = models.CharField(max_length=100, default='direct')
    calculated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-calculated_at']
        verbose_name = 'Métrique'
        verbose_name_plural = 'Métriques'
        indexes = [
            models.Index(fields=['client', 'name']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"
