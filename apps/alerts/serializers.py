"""
Serializers for the alerts application.
"""
from rest_framework import serializers
from .models import Alert, AlertComment, AlertAttachment, AlertRule
from apps.accounts.serializers import UserSerializer, ClientSerializer


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    severity_color = serializers.CharField(source='get_severity_color', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    resolution_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'title', 'description', 'alert_type', 'alert_type_display',
            'severity', 'severity_display', 'severity_color', 'status', 'status_display',
            'status_color', 'source_ip', 'destination_ip', 'source_port', 'destination_port',
            'protocol', 'source_system', 'raw_data', 'tags', 'detected_at', 'created_at',
            'updated_at', 'closed_at', 'assigned_to', 'assigned_to_name', 'risk_score',
            'risk_factors', 'client', 'client_name', 'resolution_time'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_resolution_time(self, obj):
        """Get resolution time in minutes."""
        return obj.get_resolution_time()


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating alerts."""
    
    class Meta:
        model = Alert
        fields = [
            'alert_id', 'title', 'description', 'alert_type', 'severity',
            'source_ip', 'destination_ip', 'source_port', 'destination_port',
            'protocol', 'source_system', 'raw_data', 'tags', 'detected_at',
            'risk_score', 'risk_factors', 'client'
        ]
    
    def create(self, validated_data):
        """Create alert and automatically assign client based on user role."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            
            # For SOC analysts and admins, they can specify client
            # For clients, automatically use their client
            if user.role == 'client' and user.client:
                validated_data['client'] = user.client
            elif 'client' not in validated_data:
                # If no client specified and user is not a client, raise error
                raise serializers.ValidationError("Client must be specified for this user role.")
        
        # Set default status to 'in_progress' as per requirements
        validated_data['status'] = 'in_progress'
        
        return super().create(validated_data)


class AlertUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating alerts."""
    
    class Meta:
        model = Alert
        fields = [
            'status', 'assigned_to', 'risk_score', 'risk_factors', 'tags'
        ]


class AlertCommentSerializer(serializers.ModelSerializer):
    """Serializer for AlertComment model."""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    
    class Meta:
        model = AlertComment
        fields = [
            'id', 'alert', 'author', 'author_name', 'author_email', 'content',
            'is_internal', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class AlertAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for AlertAttachment model."""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    
    class Meta:
        model = AlertAttachment
        fields = [
            'id', 'alert', 'file', 'filename', 'file_size', 'mime_type',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'uploaded_at']


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'is_active', 'alert_types', 'severity_levels',
            'source_ips', 'destination_ips', 'keywords', 'min_risk_score', 'max_risk_score',
            'notify_email', 'notify_dashboard', 'email_recipients', 'client', 'client_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class AlertRuleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating alert rules."""
    
    class Meta:
        model = AlertRule
        fields = [
            'name', 'description', 'is_active', 'alert_types', 'severity_levels',
            'source_ips', 'destination_ips', 'keywords', 'min_risk_score', 'max_risk_score',
            'notify_email', 'notify_dashboard', 'email_recipients'
        ]
    
    def create(self, validated_data):
        """Create alert rule and automatically assign client based on user role."""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            
            # For SOC analysts and admins, they can specify client
            # For clients, automatically use their client
            if user.role == 'client' and user.client:
                validated_data['client'] = user.client
            elif 'client' not in validated_data:
                # If no client specified and user is not a client, raise error
                raise serializers.ValidationError("Client must be specified for this user role.")
        
        return super().create(validated_data)


class AlertStatisticsSerializer(serializers.Serializer):
    """Serializer for alert statistics."""
    
    total_alerts = serializers.IntegerField()
    open_alerts = serializers.IntegerField()
    in_progress_alerts = serializers.IntegerField()
    closed_alerts = serializers.IntegerField()
    false_positive_alerts = serializers.IntegerField()
    
    # By severity
    low_severity = serializers.IntegerField()
    medium_severity = serializers.IntegerField()
    high_severity = serializers.IntegerField()
    critical_severity = serializers.IntegerField()
    
    # By type
    alert_types = serializers.DictField()
    
    # Risk score distribution
    avg_risk_score = serializers.FloatField()
    max_risk_score = serializers.FloatField()
    min_risk_score = serializers.FloatField()
    
    # Time-based statistics
    alerts_last_24h = serializers.IntegerField()
    alerts_last_7d = serializers.IntegerField()
    alerts_last_30d = serializers.IntegerField()
