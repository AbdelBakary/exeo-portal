from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Incident, IncidentComment, IncidentAttachment, IncidentTimeline
from .serializers import (
    IncidentSerializer, 
    IncidentCommentSerializer, 
    IncidentAttachmentSerializer,
    IncidentTimelineSerializer
)
from apps.accounts.permissions import IsClientOwner, IsAdminOrAnalyst


class IncidentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing incidents
    """
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'incident_id', 'category']
    ordering_fields = ['reported_at', 'priority', 'impact_score', 'status']
    ordering = ['-reported_at']
    
    def get_queryset(self):
        """Filter incidents based on user role and client"""
        if self.request.user.role in ['admin', 'soc_analyst']:
            return Incident.objects.all()
        elif self.request.user.role == 'client':
            return Incident.objects.filter(client=self.request.user.client)
        return Incident.objects.none()
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminOrAnalyst]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics for incidents"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        queryset = queryset.filter(reported_at__gte=start_date)
        
        stats = {
            'total_incidents': queryset.count(),
            'open_incidents': queryset.filter(status__in=['new', 'assigned', 'in_progress']).count(),
            'resolved_incidents': queryset.filter(status='resolved').count(),
            'closed_incidents': queryset.filter(status='closed').count(),
            'critical_incidents': queryset.filter(priority='critical').count(),
            'high_priority_incidents': queryset.filter(priority='high').count(),
            'avg_resolution_time': self._calculate_avg_resolution_time(queryset),
            'incidents_by_category': self._get_incidents_by_category(queryset),
            'incidents_by_priority': self._get_incidents_by_priority(queryset),
            'incidents_by_status': self._get_incidents_by_status(queryset),
            'trend_data': self._get_trend_data(queryset, days)
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to an incident"""
        incident = self.get_object()
        serializer = IncidentCommentSerializer(data=request.data)
        
        if serializer.is_valid():
            comment = serializer.save(
                incident=incident,
                author=request.user
            )
            
            # Create timeline event
            IncidentTimeline.objects.create(
                incident=incident,
                event_type='comment_added',
                description=f'Commentaire ajouté par {request.user.email}',
                user=request.user
            )
            
            return Response(IncidentCommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change incident status"""
        incident = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Incident.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        old_status = incident.status
        incident.status = new_status
        incident.save()
        
        # Create timeline event
        IncidentTimeline.objects.create(
            incident=incident,
            event_type='status_changed',
            description=f'Statut changé de {old_status} à {new_status}',
            user=request.user,
            metadata={'old_status': old_status, 'new_status': new_status}
        )
        
        return Response(IncidentSerializer(incident).data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign incident to a user"""
        incident = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.accounts.models import User
            assigned_user = User.objects.get(id=assigned_to_id)
            incident.assigned_to = assigned_user
            incident.assigned_by = request.user
            incident.status = 'assigned'
            incident.save()
            
            # Create timeline event
            IncidentTimeline.objects.create(
                incident=incident,
                event_type='assigned',
                description=f'Incident assigné à {assigned_user.email}',
                user=request.user
            )
            
            return Response(IncidentSerializer(incident).data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _calculate_avg_resolution_time(self, queryset):
        """Calculate average resolution time in hours"""
        resolved_incidents = queryset.filter(
            status='resolved',
            resolved_at__isnull=False
        )
        
        if not resolved_incidents.exists():
            return 0
        
        total_hours = 0
        count = 0
        
        for incident in resolved_incidents:
            if incident.resolved_at and incident.detected_at:
                resolution_time = incident.resolved_at - incident.detected_at
                total_hours += resolution_time.total_seconds() / 3600
                count += 1
        
        return round(total_hours / count, 2) if count > 0 else 0
    
    def _get_incidents_by_category(self, queryset):
        """Get incident count by category"""
        return list(queryset.values('category').annotate(count=Count('id')).order_by('-count'))
    
    def _get_incidents_by_priority(self, queryset):
        """Get incident count by priority"""
        return list(queryset.values('priority').annotate(count=Count('id')).order_by('-count'))
    
    def _get_incidents_by_status(self, queryset):
        """Get incident count by status"""
        return list(queryset.values('status').annotate(count=Count('id')).order_by('-count'))
    
    def _get_trend_data(self, queryset, days):
        """Get incident trend data over time"""
        from django.db.models.functions import TruncDay
        
        trend_data = list(
            queryset.annotate(day=TruncDay('reported_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        return trend_data


class IncidentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing incident comments"""
    serializer_class = IncidentCommentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        incident_id = self.kwargs.get('incident_pk')
        return IncidentComment.objects.filter(incident_id=incident_id)
    
    def perform_create(self, serializer):
        incident_id = self.kwargs.get('incident_pk')
        incident = Incident.objects.get(id=incident_id)
        serializer.save(incident=incident, author=self.request.user)


class IncidentAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing incident attachments"""
    serializer_class = IncidentAttachmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        incident_id = self.kwargs.get('incident_pk')
        return IncidentAttachment.objects.filter(incident_id=incident_id)
    
    def perform_create(self, serializer):
        incident_id = self.kwargs.get('incident_pk')
        incident = Incident.objects.get(id=incident_id)
        serializer.save(incident=incident, uploaded_by=self.request.user)


class IncidentTimelineViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing incident timeline"""
    serializer_class = IncidentTimelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        incident_id = self.kwargs.get('incident_pk')
        return IncidentTimeline.objects.filter(incident_id=incident_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats_view(request):
    """Simple view for dashboard stats"""
    from django.db.models import Q, Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Get incidents based on user role
    if request.user.role in ['admin', 'soc_analyst']:
        queryset = Incident.objects.all()
    elif request.user.role == 'client':
        queryset = Incident.objects.filter(client=request.user.client)
    else:
        queryset = Incident.objects.none()
    
    # Filter by date range if provided
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    queryset = queryset.filter(reported_at__gte=start_date)
    
    stats = {
        'total_incidents': queryset.count(),
        'open_incidents': queryset.filter(status__in=['new', 'assigned', 'in_progress']).count(),
        'resolved_incidents': queryset.filter(status='resolved').count(),
        'closed_incidents': queryset.filter(status='closed').count(),
        'critical_incidents': queryset.filter(priority='critical').count(),
        'high_priority_incidents': queryset.filter(priority='high').count(),
        'avg_resolution_time': 0,  # Simplified for now
        'incidents_by_category': [],
        'incidents_by_priority': [],
        'incidents_by_status': [],
        'trend_data': []
    }
    
    return Response(stats)
