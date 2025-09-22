"""
Admin configuration for the tickets application.
"""
from django.contrib import admin
from .models import (
    ClientTicket, TicketComment, TicketAttachment, 
    TicketTimeline, TicketTemplate, TicketSLA
)


@admin.register(ClientTicket)
class ClientTicketAdmin(admin.ModelAdmin):
    """Admin for ClientTicket model."""
    
    list_display = [
        'ticket_id', 'title', 'client', 'created_by', 'category', 
        'priority', 'status', 'assigned_to', 'created_at'
    ]
    list_filter = [
        'category', 'priority', 'status', 'client', 'created_at', 'assigned_to'
    ]
    search_fields = ['ticket_id', 'title', 'description', 'client__name']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('ticket_id', 'client', 'created_by')
        }),
        ('Contenu', {
            'fields': ('title', 'description', 'category', 'priority', 'status')
        }),
        ('Gestion SOC', {
            'fields': ('assigned_to', 'assigned_by')
        }),
        ('Relations', {
            'fields': ('related_alert', 'related_incident'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('tags', 'custom_fields'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('SLA et Métriques', {
            'fields': ('sla_deadline', 'first_response_at', 'resolution_time_hours'),
            'classes': ('collapse',)
        }),
        ('Satisfaction Client', {
            'fields': ('client_rating', 'client_feedback'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter tickets based on user role."""
        qs = super().get_queryset(request)
        
        if request.user.role == 'client' and request.user.client:
            return qs.filter(client=request.user.client)
        
        return qs


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """Admin for TicketComment model."""
    
    list_display = ['ticket', 'author', 'comment_type', 'is_internal', 'created_at']
    list_filter = ['comment_type', 'is_internal', 'created_at']
    search_fields = ['ticket__ticket_id', 'author__email', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    """Admin for TicketAttachment model."""
    
    list_display = ['ticket', 'filename', 'file_size', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'mime_type']
    search_fields = ['ticket__ticket_id', 'filename', 'uploaded_by__email']
    readonly_fields = ['uploaded_at']


@admin.register(TicketTimeline)
class TicketTimelineAdmin(admin.ModelAdmin):
    """Admin for TicketTimeline model."""
    
    list_display = ['ticket', 'event_type', 'user', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['ticket__ticket_id', 'description', 'user__email']
    readonly_fields = ['created_at']


@admin.register(TicketTemplate)
class TicketTemplateAdmin(admin.ModelAdmin):
    """Admin for TicketTemplate model."""
    
    list_display = ['name', 'client', 'template_type', 'category', 'priority', 'is_active']
    list_filter = ['template_type', 'category', 'priority', 'is_active', 'is_public']
    search_fields = ['name', 'description', 'client__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TicketSLA)
class TicketSLAAdmin(admin.ModelAdmin):
    """Admin for TicketSLA model."""
    
    list_display = [
        'name', 'client', 'first_response_time', 'resolution_time', 
        'escalation_time', 'is_active'
    ]
    list_filter = ['is_active', 'client', 'created_at']
    search_fields = ['name', 'description', 'client__name']
    readonly_fields = ['created_at', 'updated_at']