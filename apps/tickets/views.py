"""
Views for the tickets application.
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters

from .models import (
    ClientTicket, TicketComment, TicketAttachment, 
    TicketTimeline, TicketTemplate, TicketSLA
)
from .serializers import (
    ClientTicketSerializer, ClientTicketCreateSerializer, ClientTicketUpdateSerializer,
    TicketCommentSerializer, TicketAttachmentSerializer, TicketTimelineSerializer,
    TicketTemplateSerializer, TicketSLASerializer, TicketStatisticsSerializer,
    TicketDashboardSerializer
)
from .permissions import (
    CanCreateTicket, CanViewClientTickets, CanModifyTicket, CanAssignTicket,
    CanViewAllTickets, CanManageTicketTemplates, CanManageTicketSLA,
    IsTicketOwnerOrSOC, CanAddTicketComment, CanUploadTicketAttachment
)


class TicketFilter(django_filters.FilterSet):
    """Filter for ClientTicket model."""
    
    category = django_filters.ChoiceFilter(choices=ClientTicket.CATEGORY_CHOICES)
    priority = django_filters.ChoiceFilter(choices=ClientTicket.PRIORITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=ClientTicket.STATUS_CHOICES)
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to')
    created_by = django_filters.NumberFilter(field_name='created_by')
    
    class Meta:
        model = ClientTicket
        fields = ['category', 'priority', 'status', 'created_after', 'created_before', 'assigned_to', 'created_by']


class MyTicketsView(generics.ListCreateAPIView):
    """
    View for client users to see their own tickets and create new ones.
    Port 3000 - Espace Client
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['title', 'description', 'ticket_id']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClientTicketCreateSerializer
        return ClientTicketSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['admin', 'soc_analyst']:
            # Admin and SOC can see all tickets
            return ClientTicket.objects.all()
        elif user.role == 'client':
            if user.client:
                # Clients can only see tickets from their organization
                return ClientTicket.objects.filter(client=user.client)
            else:
                # If client user has no client assigned, return empty queryset
                return ClientTicket.objects.none()
        
        return ClientTicket.objects.none()
    
    def has_permission(self, request, view):
        """Check if user has permission to access this view."""
        user = request.user
        
        # Admin and SOC analysts can access all tickets
        if user.role in ['admin', 'soc_analyst']:
            return True
        
        # Client users can access tickets (even if no client assigned, they'll see empty list)
        if user.role == 'client':
            return True
        
        return False
    
    def perform_create(self, serializer):
        serializer.save()


class AllTicketsView(generics.ListAPIView):
    """
    View for SOC analysts to see all tickets.
    Port 8000 - Espace SOC
    """
    permission_classes = [IsAuthenticated, CanViewAllTickets]
    serializer_class = ClientTicketSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['title', 'description', 'ticket_id', 'client__name']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ClientTicket.objects.all()


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for ticket details, updates and deletion.
    """
    permission_classes = [IsAuthenticated, IsTicketOwnerOrSOC, CanModifyTicket]
    serializer_class = ClientTicketSerializer
    lookup_field = 'ticket_id'
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role in ['admin', 'soc_analyst']:
            return ClientTicket.objects.all()
        elif user.role == 'client':
            return ClientTicket.objects.filter(client=user.client)
        
        return ClientTicket.objects.none()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClientTicketUpdateSerializer
        return ClientTicketSerializer
    
    def perform_update(self, serializer):
        # Log the status change
        if 'status' in serializer.validated_data:
            old_status = self.get_object().status
            new_status = serializer.validated_data['status']
            if old_status != new_status:
                TicketTimeline.objects.create(
                    ticket=self.get_object(),
                    event_type='status_change',
                    description=f'Statut changé de {old_status} à {new_status}',
                    user=self.request.user,
                    metadata={'old_status': old_status, 'new_status': new_status}
                )
        serializer.save()


class AssignTicketView(generics.UpdateAPIView):
    """
    View for assigning tickets to SOC analysts.
    Port 8000 - Espace SOC
    """
    permission_classes = [IsAuthenticated, CanAssignTicket]
    serializer_class = ClientTicketUpdateSerializer
    
    def get_queryset(self):
        return ClientTicket.objects.all()
    
    def perform_update(self, serializer):
        serializer.save(assigned_by=self.request.user)


class TicketCommentViewSet(generics.ListCreateAPIView):
    """
    View for ticket comments.
    """
    permission_classes = [IsAuthenticated, CanAddTicketComment]
    serializer_class = TicketCommentSerializer
    
    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return TicketComment.objects.filter(ticket__ticket_id=ticket_id)
    
    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        try:
            ticket = ClientTicket.objects.get(ticket_id=ticket_id)
            # Vérifier que l'utilisateur peut accéder à ce ticket
            if not ticket.can_be_accessed_by(self.request.user):
                raise serializers.ValidationError("Vous n'avez pas la permission d'ajouter un commentaire à ce ticket")
            serializer.save(ticket=ticket, author=self.request.user)
        except ClientTicket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found")


class TicketAttachmentViewSet(generics.ListCreateAPIView):
    """
    View for ticket attachments.
    """
    permission_classes = [IsAuthenticated, CanUploadTicketAttachment]
    serializer_class = TicketAttachmentSerializer
    
    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return TicketAttachment.objects.filter(ticket__ticket_id=ticket_id)
    
    def perform_create(self, serializer):
        ticket_id = self.kwargs.get('ticket_id')
        try:
            ticket = ClientTicket.objects.get(ticket_id=ticket_id)
            serializer.save(ticket=ticket)
        except ClientTicket.DoesNotExist:
            raise serializers.ValidationError("Ticket not found")


class TicketTimelineView(generics.ListAPIView):
    """
    View for ticket timeline.
    """
    permission_classes = [IsAuthenticated, IsTicketOwnerOrSOC]
    serializer_class = TicketTimelineSerializer
    
    def get_queryset(self):
        ticket_id = self.kwargs.get('ticket_id')
        return TicketTimeline.objects.filter(ticket__ticket_id=ticket_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanViewAllTickets])
def ticket_statistics(request):
    """
    Get ticket statistics for dashboard.
    """
    # Base queryset
    queryset = ClientTicket.objects.all()
    
    # Filter by client if specified
    client_id = request.query_params.get('client_id')
    if client_id:
        queryset = queryset.filter(client_id=client_id)
    
    # Calculate statistics
    total_tickets = queryset.count()
    open_tickets = queryset.filter(status='open').count()
    in_progress_tickets = queryset.filter(status='in_progress').count()
    resolved_tickets = queryset.filter(status='resolved').count()
    closed_tickets = queryset.filter(status='closed').count()
    
    # Tickets by category
    tickets_by_category = dict(queryset.values('category').annotate(count=Count('id')).values_list('category', 'count'))
    
    # Tickets by priority
    tickets_by_priority = dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count'))
    
    # Tickets by status
    tickets_by_status = dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    
    # Average resolution time
    avg_resolution_time = queryset.filter(resolution_time_hours__isnull=False).aggregate(
        avg=Avg('resolution_time_hours')
    )['avg'] or 0
    
    # Average client rating
    avg_client_rating = queryset.filter(client_rating__isnull=False).aggregate(
        avg=Avg('client_rating')
    )['avg'] or 0
    
    # Trend data (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    trend_data = []
    for i in range(30):
        date = start_date + timedelta(days=i)
        count = queryset.filter(created_at__date=date.date()).count()
        trend_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    statistics = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'tickets_by_category': tickets_by_category,
        'tickets_by_priority': tickets_by_priority,
        'tickets_by_status': tickets_by_status,
        'avg_resolution_time': round(avg_resolution_time, 2),
        'avg_client_rating': round(avg_client_rating, 2),
        'trend_data': trend_data
    }
    
    serializer = TicketStatisticsSerializer(statistics)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_dashboard(request):
    """
    Get dashboard data for tickets.
    """
    user = request.user
    
    # Recent tickets
    if user.role in ['admin', 'soc_analyst']:
        recent_tickets = ClientTicket.objects.all()[:10]
        my_assigned_tickets = ClientTicket.objects.filter(assigned_to=user)[:5]
    else:
        recent_tickets = ClientTicket.objects.filter(client=user.client)[:10]
        my_assigned_tickets = ClientTicket.objects.none()
    
    # SLA breaches
    sla_breaches = ClientTicket.objects.filter(
        sla_deadline__lt=timezone.now(),
        status__in=['open', 'in_progress']
    )[:5]
    
    # Statistics
    statistics_data = ticket_statistics(request).data
    
    dashboard_data = {
        'recent_tickets': recent_tickets,
        'my_assigned_tickets': my_assigned_tickets,
        'statistics': statistics_data,
        'sla_breaches': sla_breaches
    }
    
    serializer = TicketDashboardSerializer(dashboard_data)
    return Response(serializer.data)


class TicketTemplateViewSet(generics.ListCreateAPIView):
    """
    View for ticket templates.
    """
    permission_classes = [IsAuthenticated, CanManageTicketTemplates]
    serializer_class = TicketTemplateSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'admin':
            return TicketTemplate.objects.all()
        elif user.role == 'soc_analyst':
            return TicketTemplate.objects.filter(is_public=True)
        
        return TicketTemplate.objects.none()


class TicketSLAViewSet(generics.ListCreateAPIView):
    """
    View for ticket SLA management.
    """
    permission_classes = [IsAuthenticated, CanManageTicketSLA]
    serializer_class = TicketSLASerializer
    
    def get_queryset(self):
        return TicketSLA.objects.all()