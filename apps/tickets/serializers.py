"""
Serializers for the tickets application.
"""
from rest_framework import serializers
from .models import (
    ClientTicket, TicketComment, TicketAttachment, 
    TicketTimeline, TicketTemplate, TicketSLA
)
from apps.accounts.serializers import UserSerializer, ClientSerializer


class ClientTicketSerializer(serializers.ModelSerializer):
    """Serializer for ClientTicket model."""
    
    # Related object names
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    created_by_email = serializers.CharField(source='created_by.email', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    # Display fields
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    
    # Related objects
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    timeline_events_count = serializers.SerializerMethodField()
    
    # Related alert/incident info
    related_alert_id = serializers.CharField(source='related_alert.alert_id', read_only=True)
    related_incident_id = serializers.CharField(source='related_incident.incident_id', read_only=True)
    
    class Meta:
        model = ClientTicket
        fields = [
            'id', 'ticket_id', 'title', 'description', 'category', 'category_display',
            'priority', 'priority_display', 'priority_color', 'status', 'status_display',
            'status_color', 'tags', 'custom_fields', 'created_at', 'updated_at',
            'resolved_at', 'closed_at', 'sla_deadline', 'first_response_at',
            'resolution_time_hours', 'client_rating', 'client_feedback',
            'client', 'client_name', 'created_by', 'created_by_name', 'created_by_email',
            'assigned_to', 'assigned_to_name', 'assigned_by', 'assigned_by_name',
            'related_alert', 'related_alert_id', 'related_incident', 'related_incident_id',
            'comments_count', 'attachments_count', 'timeline_events_count'
        ]
        read_only_fields = ['id', 'ticket_id', 'created_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()
    
    def get_timeline_events_count(self, obj):
        return obj.timeline.count()


class ClientTicketCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ClientTicket."""
    
    class Meta:
        model = ClientTicket
        fields = [
            'title', 'description', 'category', 'priority', 'tags', 'custom_fields',
            'related_alert', 'related_incident'
        ]
    
    def create(self, validated_data):
        # Set the client from the authenticated user
        validated_data['client'] = self.context['request'].user.client
        validated_data['created_by'] = self.context['request'].user
        
        # Generate ticket ID
        import uuid
        validated_data['ticket_id'] = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        
        return super().create(validated_data)


class ClientTicketUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating ClientTicket."""
    
    class Meta:
        model = ClientTicket
        fields = [
            'title', 'description', 'category', 'priority', 'status', 'tags',
            'custom_fields', 'assigned_to', 'client_rating', 'client_feedback'
        ]
        read_only_fields = ['ticket_id', 'client', 'created_by']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serializer for TicketComment model."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    comment_type_display = serializers.CharField(source='get_comment_type_display', read_only=True)
    
    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'author', 'author_name', 'author_email', 'content',
            'comment_type', 'comment_type_display', 'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ticket', 'author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class TicketAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for TicketAttachment model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = TicketAttachment
        fields = [
            'id', 'ticket', 'file', 'filename', 'file_size', 'mime_type',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class TicketTimelineSerializer(serializers.ModelSerializer):
    """Serializer for TicketTimeline model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = TicketTimeline
        fields = [
            'id', 'ticket', 'event_type', 'event_type_display', 'description',
            'user', 'user_name', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TicketTemplateSerializer(serializers.ModelSerializer):
    """Serializer for TicketTemplate model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = TicketTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'template_type_display',
            'title_template', 'description_template', 'category', 'category_display',
            'priority', 'priority_display', 'is_active', 'is_public',
            'client', 'client_name', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TicketSLASerializer(serializers.ModelSerializer):
    """Serializer for TicketSLA model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    escalate_to_name = serializers.CharField(source='escalate_to.get_full_name', read_only=True)
    
    class Meta:
        model = TicketSLA
        fields = [
            'id', 'name', 'description', 'categories', 'priorities',
            'first_response_time', 'resolution_time', 'escalation_time',
            'escalate_to', 'escalate_to_name', 'is_active',
            'client', 'client_name', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class TicketStatisticsSerializer(serializers.Serializer):
    """Serializer for ticket statistics."""
    
    total_tickets = serializers.IntegerField()
    open_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    closed_tickets = serializers.IntegerField()
    
    tickets_by_category = serializers.DictField()
    tickets_by_priority = serializers.DictField()
    tickets_by_status = serializers.DictField()
    
    avg_resolution_time = serializers.FloatField()
    avg_client_rating = serializers.FloatField()
    
    trend_data = serializers.ListField()


class TicketDashboardSerializer(serializers.Serializer):
    """Serializer for ticket dashboard data."""
    
    recent_tickets = ClientTicketSerializer(many=True)
    my_assigned_tickets = ClientTicketSerializer(many=True)
    statistics = TicketStatisticsSerializer()
    sla_breaches = ClientTicketSerializer(many=True)
