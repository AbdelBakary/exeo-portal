"""
Models for the tickets application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models import Client, User
from apps.alerts.models import Alert
from apps.incidents.models import Incident


class ClientTicket(models.Model):
    """Model representing a client support ticket."""
    
    CATEGORY_CHOICES = [
        ('support', 'Support technique'),
        ('incident', 'Incident de sécurité'),
        ('feature_request', 'Demande de fonctionnalité'),
        ('account', 'Gestion de compte'),
        ('billing', 'Facturation'),
        ('training', 'Formation'),
        ('consultation', 'Consultation'),
        ('other', 'Autre'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('in_progress', 'En cours'),
        ('waiting_client', 'En attente client'),
        ('waiting_soc', 'En attente SOC'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
        ('cancelled', 'Annulé'),
    ]
    
    # Identification
    ticket_id = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='tickets')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_tickets'
    )
    
    # Contenu
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Gestion SOC
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets_by'
    )
    
    # Relations avec l'écosystème existant
    related_alert = models.ForeignKey(
        Alert, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tickets'
    )
    related_incident = models.ForeignKey(
        Incident, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tickets'
    )
    
    # Métadonnées
    tags = models.JSONField(default=list, blank=True)
    custom_fields = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    
    # SLA et métriques
    sla_deadline = models.DateTimeField(blank=True, null=True)
    first_response_at = models.DateTimeField(blank=True, null=True)
    resolution_time_hours = models.FloatField(blank=True, null=True)
    
    # Satisfaction client
    client_rating = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    client_feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Ticket client'
        verbose_name_plural = 'Tickets clients'
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['client', 'priority']),
            models.Index(fields=['client', 'category']),
            models.Index(fields=['created_by']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ticket_id']),
        ]
    
    def __str__(self):
        return f"{self.ticket_id} - {self.title} ({self.get_status_display()})"
    
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
            'open': '#dc3545',
            'in_progress': '#17a2b8',
            'waiting_client': '#ffc107',
            'waiting_soc': '#6f42c1',
            'resolved': '#28a745',
            'closed': '#6c757d',
            'cancelled': '#6c757d',
        }
        return colors.get(self.status, '#6c757d')
    
    def can_be_accessed_by(self, user):
        """Check if user can access this ticket."""
        # Admin and SOC analysts can access all tickets
        if user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can only access tickets from their organization
        if user.role == 'client' and user.client == self.client:
            return True
        
        return False
    
    def can_be_modified_by(self, user):
        """Check if user can modify this ticket."""
        # Admin and SOC analysts can modify all tickets
        if user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can only modify their own tickets if they are open
        if (user.role == 'client' and 
            user.client == self.client and 
            user == self.created_by and 
            self.status in ['open', 'waiting_client']):
            return True
        
        return False


class TicketComment(models.Model):
    """Model for comments on tickets."""
    
    COMMENT_TYPES = [
        ('client', 'Client'),
        ('soc', 'SOC'),
        ('system', 'Système'),
    ]
    
    ticket = models.ForeignKey(ClientTicket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='client')
    is_internal = models.BooleanField(default=False)  # Internal SOC comments
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Commentaire de ticket'
        verbose_name_plural = 'Commentaires de tickets'
    
    def __str__(self):
        return f"Commentaire sur {self.ticket.ticket_id} par {self.author.email}"


class TicketAttachment(models.Model):
    """Model for file attachments on tickets."""
    
    ticket = models.ForeignKey(ClientTicket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/')
    filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Pièce jointe de ticket'
        verbose_name_plural = 'Pièces jointes de tickets'
    
    def __str__(self):
        return f"{self.filename} - {self.ticket.ticket_id}"


class TicketTimeline(models.Model):
    """Model for tracking ticket timeline events."""
    
    EVENT_TYPES = [
        ('created', 'Créé'),
        ('assigned', 'Assigné'),
        ('status_changed', 'Statut modifié'),
        ('priority_changed', 'Priorité modifiée'),
        ('comment_added', 'Commentaire ajouté'),
        ('attachment_added', 'Pièce jointe ajoutée'),
        ('resolved', 'Résolu'),
        ('closed', 'Fermé'),
        ('reopened', 'Rouvert'),
        ('escalated', 'Escaladé'),
    ]
    
    ticket = models.ForeignKey(ClientTicket, on_delete=models.CASCADE, related_name='timeline')
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
        return f"{self.ticket.ticket_id} - {self.get_event_type_display()}"


class TicketTemplate(models.Model):
    """Model for ticket templates."""
    
    TEMPLATE_TYPES = [
        ('incident', 'Incident de sécurité'),
        ('support', 'Support technique'),
        ('feature_request', 'Demande de fonctionnalité'),
        ('training', 'Formation'),
        ('consultation', 'Consultation'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ticket_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPES)
    
    # Template content
    title_template = models.CharField(max_length=200)
    description_template = models.TextField()
    category = models.CharField(max_length=50, choices=ClientTicket.CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=ClientTicket.PRIORITY_CHOICES)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)  # Available to all clients
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ticket_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Modèle de ticket'
        verbose_name_plural = 'Modèles de tickets'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"


class TicketSLA(models.Model):
    """Model for ticket SLA (Service Level Agreement) rules."""
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ticket_slas')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # SLA criteria
    categories = models.JSONField(default=list, blank=True)
    priorities = models.JSONField(default=list, blank=True)
    
    # SLA times (in hours)
    first_response_time = models.PositiveIntegerField(default=4)  # 4 hours
    resolution_time = models.PositiveIntegerField(default=24)     # 24 hours
    
    # Escalation
    escalation_time = models.PositiveIntegerField(default=48)     # 48 hours
    escalate_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escalated_tickets',
        null=True,
        blank=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_ticket_slas')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'SLA de ticket'
        verbose_name_plural = 'SLAs de tickets'
    
    def __str__(self):
        return f"{self.name} - {self.client.name}"