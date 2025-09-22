"""
Views for the alerts application.
"""
from django.db.models import Count, Avg, Max, Min, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import Alert, AlertComment, AlertAttachment, AlertRule
from .serializers import (
    AlertSerializer, AlertCreateSerializer, AlertUpdateSerializer,
    AlertCommentSerializer, AlertAttachmentSerializer, AlertRuleSerializer,
    AlertRuleCreateSerializer, AlertStatisticsSerializer
)
from apps.accounts.permissions import CanAccessClientData


class AlertFilter(django_filters.FilterSet):
    """Filter for Alert model."""
    
    severity = django_filters.MultipleChoiceFilter(choices=Alert.SEVERITY_CHOICES)
    status = django_filters.MultipleChoiceFilter(choices=Alert.STATUS_CHOICES)
    alert_type = django_filters.MultipleChoiceFilter(choices=Alert.TYPE_CHOICES)
    min_risk_score = django_filters.NumberFilter(field_name='risk_score', lookup_expr='gte')
    max_risk_score = django_filters.NumberFilter(field_name='risk_score', lookup_expr='lte')
    detected_after = django_filters.DateTimeFilter(field_name='detected_at', lookup_expr='gte')
    detected_before = django_filters.DateTimeFilter(field_name='detected_at', lookup_expr='lte')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to')
    has_attachments = django_filters.BooleanFilter(method='filter_has_attachments')
    
    class Meta:
        model = Alert
        fields = ['severity', 'status', 'alert_type', 'min_risk_score', 'max_risk_score',
                 'detected_after', 'detected_before', 'assigned_to', 'has_attachments']
    
    def filter_has_attachments(self, queryset, name, value):
        """Filter alerts that have or don't have attachments."""
        if value:
            return queryset.filter(attachments__isnull=False).distinct()
        else:
            return queryset.filter(attachments__isnull=True)


class AlertListCreateView(generics.ListCreateAPIView):
    """View for listing and creating alerts."""
    
    serializer_class = AlertSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AlertFilter
    search_fields = ['title', 'description', 'alert_id', 'source_ip', 'destination_ip']
    ordering_fields = ['detected_at', 'created_at', 'risk_score', 'severity']
    ordering = ['-detected_at']
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return AlertCreateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        """Filter alerts based on user role and client."""
        queryset = Alert.objects.select_related('client', 'assigned_to').all()
        
        # If user is a client, only show alerts from their client
        if self.request.user.role == 'client':
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset


class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for alert detail operations."""
    
    queryset = Alert.objects.select_related('client', 'assigned_to')
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return AlertUpdateSerializer
        return AlertSerializer


class AlertCommentListCreateView(generics.ListCreateAPIView):
    """View for listing and creating alert comments."""
    
    serializer_class = AlertCommentSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_queryset(self):
        """Filter comments based on alert and user permissions."""
        alert_id = self.kwargs['alert_id']
        return AlertComment.objects.filter(alert_id=alert_id).select_related('author')
    
    def perform_create(self, serializer):
        """Set the author and alert for the comment."""
        alert_id = self.kwargs['alert_id']
        alert = Alert.objects.get(id=alert_id)
        serializer.save(author=self.request.user, alert=alert)


class AlertAttachmentListCreateView(generics.ListCreateAPIView):
    """View for listing and creating alert attachments."""
    
    serializer_class = AlertAttachmentSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_queryset(self):
        """Filter attachments based on alert and user permissions."""
        alert_id = self.kwargs['alert_id']
        return AlertAttachment.objects.filter(alert_id=alert_id).select_related('uploaded_by')
    
    def perform_create(self, serializer):
        """Set the uploader and alert for the attachment."""
        alert_id = self.kwargs['alert_id']
        alert = Alert.objects.get(id=alert_id)
        file = serializer.validated_data['file']
        
        serializer.save(
            uploaded_by=self.request.user,
            alert=alert,
            filename=file.name,
            file_size=file.size,
            mime_type=file.content_type
        )


class AlertRuleListCreateView(generics.ListCreateAPIView):
    """View for listing and creating alert rules."""
    
    serializer_class = AlertRuleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'client']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = [IsAuthenticated, CanAccessClientData]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return AlertRuleCreateSerializer
        return AlertRuleSerializer
    
    def get_queryset(self):
        """Filter rules based on user role and client."""
        queryset = AlertRule.objects.select_related('client', 'created_by').all()
        
        # If user is a client, only show rules from their client
        if self.request.user.role == 'client':
            queryset = queryset.filter(client=self.request.user.client)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set the creator for the rule."""
        serializer.save(created_by=self.request.user)


class AlertRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for alert rule detail operations."""
    
    queryset = AlertRule.objects.select_related('client', 'created_by')
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, CanAccessClientData]


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def alert_statistics(request):
    """Get alert statistics for dashboard."""
    
    # Base queryset
    queryset = Alert.objects.all()
    
    # If user is a client, only show their client's alerts
    if request.user.role == 'client':
        queryset = queryset.filter(client=request.user.client)
    
    # Time filters
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    # Basic counts
    total_alerts = queryset.count()
    open_alerts = queryset.filter(status='open').count()
    in_progress_alerts = queryset.filter(status='in_progress').count()
    closed_alerts = queryset.filter(status='closed').count()
    false_positive_alerts = queryset.filter(status='false_positive').count()
    
    # Severity counts
    low_severity = queryset.filter(severity='low').count()
    medium_severity = queryset.filter(severity='medium').count()
    high_severity = queryset.filter(severity='high').count()
    critical_severity = queryset.filter(severity='critical').count()
    
    # Alert types
    alert_types = dict(queryset.values('alert_type').annotate(count=Count('id')).values_list('alert_type', 'count'))
    
    # Risk score statistics
    risk_stats = queryset.aggregate(
        avg_risk_score=Avg('risk_score'),
        max_risk_score=Max('risk_score'),
        min_risk_score=Min('risk_score')
    )
    
    # Time-based statistics
    alerts_last_24h = queryset.filter(detected_at__gte=last_24h).count()
    alerts_last_7d = queryset.filter(detected_at__gte=last_7d).count()
    alerts_last_30d = queryset.filter(detected_at__gte=last_30d).count()
    
    statistics = {
        'total_alerts': total_alerts,
        'open_alerts': open_alerts,
        'in_progress_alerts': in_progress_alerts,
        'closed_alerts': closed_alerts,
        'false_positive_alerts': false_positive_alerts,
        'low_severity': low_severity,
        'medium_severity': medium_severity,
        'high_severity': high_severity,
        'critical_severity': critical_severity,
        'alert_types': alert_types,
        'avg_risk_score': risk_stats['avg_risk_score'] or 0,
        'max_risk_score': risk_stats['max_risk_score'] or 0,
        'min_risk_score': risk_stats['min_risk_score'] or 0,
        'alerts_last_24h': alerts_last_24h,
        'alerts_last_7d': alerts_last_7d,
        'alerts_last_30d': alerts_last_30d,
    }
    
    serializer = AlertStatisticsSerializer(statistics)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def bulk_update_alerts(request):
    """Bulk update multiple alerts."""
    
    alert_ids = request.data.get('alert_ids', [])
    updates = request.data.get('updates', {})
    
    if not alert_ids:
        return Response({'error': 'No alert IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filter alerts based on user permissions
    queryset = Alert.objects.filter(id__in=alert_ids)
    if request.user.role == 'client':
        queryset = queryset.filter(client=request.user.client)
    
    # Update alerts
    updated_count = queryset.update(**updates)
    
    return Response({
        'message': f'Updated {updated_count} alerts',
        'updated_count': updated_count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, CanAccessClientData])
def assign_alert(request, pk):
    """Assign an alert to a user."""
    
    try:
        alert = Alert.objects.get(pk=pk)
        
        # Check permissions
        if request.user.role == 'client' and alert.client != request.user.client:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        assigned_to_id = request.data.get('assigned_to')
        if assigned_to_id:
            from apps.accounts.models import User
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                alert.assigned_to = assigned_user
                alert.save()
                return Response({'message': 'Alert assigned successfully'})
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'assigned_to is required'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
