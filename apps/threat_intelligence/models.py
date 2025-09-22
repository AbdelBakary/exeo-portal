"""
Models for the threat intelligence application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import Client


class ThreatSource(models.Model):
    """Model representing a threat intelligence source."""
    
    SOURCE_TYPES = [
        ('misp', 'MISP'),
        ('cert_fr', 'CERT-FR'),
        ('osint', 'OSINT'),
        ('commercial', 'Commercial'),
        ('government', 'Gouvernemental'),
        ('internal', 'Interne'),
        ('other', 'Autre'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    api_endpoint = models.URLField(blank=True)
    api_key = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(blank=True, null=True)
    sync_frequency_hours = models.PositiveIntegerField(default=24)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Source de threat intelligence'
        verbose_name_plural = 'Sources de threat intelligence'
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class ThreatIndicator(models.Model):
    """Model representing a threat indicator."""
    
    INDICATOR_TYPES = [
        ('ip', 'Adresse IP'),
        ('domain', 'Nom de domaine'),
        ('url', 'URL'),
        ('email', 'Adresse email'),
        ('hash_md5', 'Hash MD5'),
        ('hash_sha1', 'Hash SHA1'),
        ('hash_sha256', 'Hash SHA256'),
        ('filename', 'Nom de fichier'),
        ('cve', 'CVE'),
        ('malware_family', 'Famille de malware'),
        ('other', 'Autre'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    source = models.ForeignKey(ThreatSource, on_delete=models.CASCADE, related_name='indicators')
    indicator_type = models.CharField(max_length=50, choices=INDICATOR_TYPES)
    value = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS, default='medium')
    
    # Threat metadata
    threat_type = models.CharField(max_length=100, blank=True)
    malware_family = models.CharField(max_length=100, blank=True)
    campaign = models.CharField(max_length=200, blank=True)
    actor = models.CharField(max_length=200, blank=True)
    
    # Technical details
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    
    # Impact assessment
    severity_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    impact_description = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_false_positive = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-first_seen']
        verbose_name = 'Indicateur de menace'
        verbose_name_plural = 'Indicateurs de menace'
        indexes = [
            models.Index(fields=['indicator_type', 'value']),
            models.Index(fields=['threat_type']),
            models.Index(fields=['confidence']),
            models.Index(fields=['first_seen']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['source', 'indicator_type', 'value']
    
    def __str__(self):
        return f"{self.get_indicator_type_display()}: {self.value}"


class ThreatCampaign(models.Model):
    """Model representing a threat campaign."""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    threat_type = models.CharField(max_length=100)
    actor = models.CharField(max_length=200, blank=True)
    target_sectors = models.JSONField(default=list, blank=True)
    target_countries = models.JSONField(default=list, blank=True)
    
    # Campaign timeline
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    is_ongoing = models.BooleanField(default=True)
    
    # Impact assessment
    severity_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    affected_organizations = models.PositiveIntegerField(default=0)
    
    # Related indicators
    indicators = models.ManyToManyField(ThreatIndicator, related_name='campaigns', blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    iocs = models.JSONField(default=dict, blank=True)  # Indicators of Compromise
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Campagne de menace'
        verbose_name_plural = 'Campagnes de menace'
    
    def __str__(self):
        return f"{self.name} ({self.threat_type})"


class ThreatIntelligenceFeed(models.Model):
    """Model for managing threat intelligence feeds."""
    
    FEED_TYPES = [
        ('ioc', 'Indicators of Compromise'),
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('vulnerability', 'Vulnérabilités'),
        ('apt', 'APT'),
        ('general', 'Général'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    feed_type = models.CharField(max_length=50, choices=FEED_TYPES)
    source = models.ForeignKey(ThreatSource, on_delete=models.CASCADE, related_name='feeds')
    
    # Feed configuration
    url = models.URLField()
    format = models.CharField(max_length=50, default='json')  # json, xml, csv, etc.
    update_frequency = models.PositiveIntegerField(default=3600)  # seconds
    is_active = models.BooleanField(default=True)
    
    # Processing settings
    auto_process = models.BooleanField(default=True)
    filter_rules = models.JSONField(default=dict, blank=True)
    mapping_rules = models.JSONField(default=dict, blank=True)
    
    # Statistics
    total_indicators = models.PositiveIntegerField(default=0)
    last_update = models.DateTimeField(blank=True, null=True)
    last_success = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Flux de threat intelligence'
        verbose_name_plural = 'Flux de threat intelligence'
    
    def __str__(self):
        return f"{self.name} ({self.get_feed_type_display()})"


class ThreatCorrelation(models.Model):
    """Model for correlating threats with client alerts."""
    
    CORRELATION_TYPES = [
        ('ip_match', 'Correspondance IP'),
        ('domain_match', 'Correspondance domaine'),
        ('hash_match', 'Correspondance hash'),
        ('email_match', 'Correspondance email'),
        ('pattern_match', 'Correspondance de pattern'),
        ('behavioral_match', 'Correspondance comportementale'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='threat_correlations')
    threat_indicator = models.ForeignKey(ThreatIndicator, on_delete=models.CASCADE, related_name='correlations')
    correlation_type = models.CharField(max_length=50, choices=CORRELATION_TYPES)
    confidence_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Related data
    matched_value = models.CharField(max_length=500)
    context = models.JSONField(default=dict, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_false_positive = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_correlations'
    )
    verification_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Corrélation de menace'
        verbose_name_plural = 'Corrélations de menace'
        unique_together = ['client', 'threat_indicator', 'correlation_type', 'matched_value']
    
    def __str__(self):
        return f"{self.client.name} - {self.threat_indicator.value} ({self.get_correlation_type_display()})"


class ThreatIntelligenceReport(models.Model):
    """Model for threat intelligence reports."""
    
    REPORT_TYPES = [
        ('daily', 'Rapport quotidien'),
        ('weekly', 'Rapport hebdomadaire'),
        ('monthly', 'Rapport mensuel'),
        ('ad_hoc', 'Rapport ad-hoc'),
        ('incident', 'Rapport d\'incident'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    content = models.TextField()
    summary = models.TextField(blank=True)
    
    # Related data
    threat_campaigns = models.ManyToManyField(ThreatCampaign, related_name='reports', blank=True)
    threat_indicators = models.ManyToManyField(ThreatIndicator, related_name='reports', blank=True)
    
    # Metadata
    severity_level = models.CharField(max_length=20, choices=ThreatIndicator.CONFIDENCE_LEVELS)
    tags = models.JSONField(default=list, blank=True)
    references = models.JSONField(default=list, blank=True)
    
    # Distribution
    is_public = models.BooleanField(default=False)
    target_clients = models.ManyToManyField(Client, related_name='threat_reports', blank=True)
    
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Rapport de threat intelligence'
        verbose_name_plural = 'Rapports de threat intelligence'
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"
