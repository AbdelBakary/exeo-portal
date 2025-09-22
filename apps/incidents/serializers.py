"""
Serializers for the incidents application.
"""
from rest_framework import serializers
from .models import (
    Incident, 
    IncidentComment, 
    IncidentAttachment, 
    IncidentTimeline,
    EscalationRule
)
from apps.accounts.serializers import UserSerializer, ClientSerializer


class IncidentSerializer(serializers.ModelSerializer):
    """Serializer for Incident model"""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.email', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.email', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    
    # Related objects
    comments_count = serializers.SerializerMethodField()
    attachments_count = serializers.SerializerMethodField()
    timeline_events_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'incident_id', 'title', 'description', 'category', 'priority', 'status',
            'client', 'client_name', 'assigned_to', 'assigned_to_name', 'assigned_by', 'assigned_by_name',
            'impact_score', 'business_impact', 'affected_systems', 'affected_users',
            'detected_at', 'reported_at', 'updated_at', 'resolved_at', 'closed_at',
            'resolution_summary', 'root_cause', 'lessons_learned', 'tags', 'custom_fields',
            'priority_display', 'status_display', 'category_display',
            'priority_color', 'status_color',
            'comments_count', 'attachments_count', 'timeline_events_count'
        ]
        read_only_fields = ['incident_id', 'reported_at', 'updated_at']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_attachments_count(self, obj):
        return obj.attachments.count()
    
    def get_timeline_events_count(self, obj):
        return obj.timeline.count()
    
    def create(self, validated_data):
        """Generate incident ID and set default values"""
        # Generate incident ID
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        client_id = validated_data['client'].id
        validated_data['incident_id'] = f"INC-{client_id}-{timestamp}"
        
        return super().create(validated_data)


class IncidentCommentSerializer(serializers.ModelSerializer):
    """Serializer for IncidentComment model"""
    
    author_name = serializers.CharField(source='author.email', read_only=True)
    author_first_name = serializers.CharField(source='author.first_name', read_only=True)
    author_last_name = serializers.CharField(source='author.last_name', read_only=True)
    
    class Meta:
        model = IncidentComment
        fields = [
            'id', 'incident', 'author', 'author_name', 'author_first_name', 'author_last_name',
            'content', 'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['incident', 'author', 'created_at', 'updated_at']


class IncidentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for IncidentAttachment model"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = IncidentAttachment
        fields = [
            'id', 'incident', 'file', 'filename', 'file_size', 'mime_type',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'file_url'
        ]
        read_only_fields = ['incident', 'uploaded_by', 'uploaded_at', 'file_size', 'mime_type']
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        """Set file metadata automatically"""
        file = validated_data['file']
        validated_data['filename'] = file.name
        validated_data['file_size'] = file.size
        validated_data['mime_type'] = file.content_type
        
        return super().create(validated_data)


class IncidentTimelineSerializer(serializers.ModelSerializer):
    """Serializer for IncidentTimeline model"""
    
    user_name = serializers.CharField(source='user.email', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = IncidentTimeline
        fields = [
            'id', 'incident', 'event_type', 'event_type_display', 'description',
            'user', 'user_name', 'metadata', 'created_at'
        ]
        read_only_fields = ['incident', 'created_at']


class EscalationRuleSerializer(serializers.ModelSerializer):
    """Serializer for EscalationRule model"""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    escalate_to_name = serializers.CharField(source='escalate_to.email', read_only=True)
    created_by_name = serializers.CharField(source='created_by.email', read_only=True)
    
    class Meta:
        model = EscalationRule
        fields = [
            'id', 'client', 'client_name', 'name', 'description', 'is_active',
            'priority_levels', 'categories', 'min_impact_score', 'time_threshold_hours',
            'escalate_to', 'escalate_to_name', 'notify_managers', 'auto_assign',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class IncidentSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for incident lists and summaries"""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.email', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    priority_color = serializers.CharField(source='get_priority_color', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'incident_id', 'title', 'category', 'priority', 'status',
            'client_name', 'assigned_to_name', 'impact_score', 'affected_users',
            'detected_at', 'reported_at', 'resolved_at',
            'priority_display', 'status_display', 'category_display',
            'priority_color', 'status_color'
        ]


class IncidentDashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_incidents = serializers.IntegerField()
    open_incidents = serializers.IntegerField()
    resolved_incidents = serializers.IntegerField()
    closed_incidents = serializers.IntegerField()
    critical_incidents = serializers.IntegerField()
    high_priority_incidents = serializers.IntegerField()
    avg_resolution_time = serializers.FloatField()
    incidents_by_category = serializers.ListField()
    incidents_by_priority = serializers.ListField()
    incidents_by_status = serializers.ListField()
    trend_data = serializers.ListField()
