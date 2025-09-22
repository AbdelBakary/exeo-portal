"""
Serializers for the analytics application.
"""
from rest_framework import serializers
from .models import RiskScore, Metric, DashboardWidget, AnalyticsEvent, ReportTemplate, GeneratedReport


class RiskScoreSerializer(serializers.ModelSerializer):
    """Serializer for RiskScore model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    calculated_by_name = serializers.CharField(source='calculated_by.get_full_name', read_only=True)
    score_type_display = serializers.CharField(source='get_score_type_display', read_only=True)
    risk_level = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskScore
        fields = [
            'id', 'client', 'client_name', 'score_type', 'score_type_display',
            'entity_id', 'entity_type', 'score', 'confidence', 'factors',
            'methodology', 'calculated_at', 'calculated_by', 'calculated_by_name',
            'risk_level'
        ]
        read_only_fields = ['id', 'calculated_at']
    
    def get_risk_level(self, obj):
        """Get risk level based on score."""
        if obj.score >= 8.0:
            return 'CRITICAL'
        elif obj.score >= 6.0:
            return 'HIGH'
        elif obj.score >= 4.0:
            return 'MEDIUM'
        elif obj.score >= 2.0:
            return 'LOW'
        else:
            return 'MINIMAL'


class MetricSerializer(serializers.ModelSerializer):
    """Serializer for Metric model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = Metric
        fields = [
            'id', 'client', 'client_name', 'name', 'metric_type', 'metric_type_display',
            'value', 'unit', 'period_start', 'period_end', 'dimensions', 'metadata',
            'calculation_method', 'calculated_at'
        ]
        read_only_fields = ['id', 'calculated_at']


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """Serializer for DashboardWidget model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    widget_type_display = serializers.CharField(source='get_widget_type_display', read_only=True)
    chart_type_display = serializers.CharField(source='get_chart_type_display', read_only=True)
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'client', 'client_name', 'name', 'description', 'widget_type',
            'widget_type_display', 'chart_type', 'chart_type_display', 'config',
            'data_source', 'refresh_interval', 'position_x', 'position_y',
            'width', 'height', 'is_visible', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for AnalyticsEvent model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'client', 'client_name', 'user', 'user_name', 'event_type',
            'event_type_display', 'page_url', 'component', 'action', 'properties',
            'session_id', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model."""
    
    client_name = serializers.CharField(source='client.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'client', 'client_name', 'name', 'description', 'report_type',
            'report_type_display', 'template_config', 'data_sources', 'filters',
            'output_format', 'schedule', 'is_scheduled', 'is_active', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class GeneratedReportSerializer(serializers.ModelSerializer):
    """Serializer for GeneratedReport model."""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'template', 'template_name', 'client', 'client_name', 'user',
            'user_name', 'title', 'status', 'status_display', 'file_path',
            'file_size', 'file_format', 'parameters', 'data_range_start',
            'data_range_end', 'requested_at', 'generated_at', 'expires_at',
            'error_message', 'retry_count'
        ]
        read_only_fields = ['id', 'requested_at']


class RiskScoreStatisticsSerializer(serializers.Serializer):
    """Serializer for risk score statistics."""
    
    overall = serializers.DictField()
    risk_levels = serializers.DictField()
    time_based = serializers.DictField()
    top_risk_factors = serializers.ListField()


class RiskScoreDistributionSerializer(serializers.Serializer):
    """Serializer for risk score distribution."""
    
    score_ranges = serializers.DictField()
    severity_distribution = serializers.DictField()
    type_distribution = serializers.DictField()


class ThreatIntelligenceSerializer(serializers.Serializer):
    """Serializer for threat intelligence data."""
    
    ip_reputation = serializers.DictField()
    domain_reputation = serializers.DictField()
    malware_family = serializers.DictField()
    threat_actor = serializers.DictField()
    campaign = serializers.DictField()
