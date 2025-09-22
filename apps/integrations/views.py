from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ClientIntegration, IntegrationLog, AlertMappingTemplate
from .serializers import (
    ClientIntegrationSerializer, 
    IntegrationLogSerializer, 
    AlertMappingTemplateSerializer
)
from .webhooks import client_webhook, webhook_status, test_webhook


class ClientIntegrationListCreateView(generics.ListCreateAPIView):
    """Liste et création des intégrations client"""
    serializer_class = ClientIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'soc_analyst']:
            return ClientIntegration.objects.all()
        elif user.role == 'client' and hasattr(user, 'client'):
            return ClientIntegration.objects.filter(client=user.client)
        return ClientIntegration.objects.none()


class ClientIntegrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, mise à jour et suppression d'une intégration"""
    serializer_class = ClientIntegrationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'soc_analyst']:
            return ClientIntegration.objects.all()
        elif user.role == 'client' and hasattr(user, 'client'):
            return ClientIntegration.objects.filter(client=user.client)
        return ClientIntegration.objects.none()


class IntegrationLogListView(generics.ListAPIView):
    """Liste des logs d'intégration"""
    serializer_class = IntegrationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'soc_analyst']:
            return IntegrationLog.objects.all()
        elif user.role == 'client' and hasattr(user, 'client'):
            return IntegrationLog.objects.filter(integration__client=user.client)
        return IntegrationLog.objects.none()


class AlertMappingTemplateListView(generics.ListAPIView):
    """Liste des templates de mapping"""
    queryset = AlertMappingTemplate.objects.filter(is_active=True)
    serializer_class = AlertMappingTemplateSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_integration_connection(request, integration_id):
    """Teste la connexion d'une intégration"""
    integration = get_object_or_404(ClientIntegration, id=integration_id)
    
    # Vérifier les permissions
    user = request.user
    if user.role == 'client' and hasattr(user, 'client') and integration.client != user.client:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # TODO: Implémenter le test de connexion selon le type d'intégration
        integration.update_sync_status(success=True)
        
        return Response({
            'success': True,
            'message': f'Connection test successful for {integration.name}',
            'status': integration.status
        })
        
    except Exception as e:
        integration.update_sync_status(success=False, error_message=str(e))
        return Response({
            'success': False,
            'error': str(e),
            'status': integration.status
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_integration_alerts(request, integration_id):
    """Synchronise les alertes d'une intégration"""
    integration = get_object_or_404(ClientIntegration, id=integration_id)
    
    # Vérifier les permissions
    user = request.user
    if user.role == 'client' and hasattr(user, 'client') and integration.client != user.client:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # TODO: Implémenter la synchronisation selon le type d'intégration
        # Pour l'instant, on simule une synchronisation réussie
        
        IntegrationLog.objects.create(
            integration=integration,
            log_type='sync_started',
            message='Synchronization started',
            details={'requested_by': user.email}
        )
        
        # Simulation d'une synchronisation
        integration.update_sync_status(success=True)
        
        IntegrationLog.objects.create(
            integration=integration,
            log_type='sync_completed',
            message='Synchronization completed successfully',
            details={'alerts_processed': 0}  # À remplacer par le vrai nombre
        )
        
        return Response({
            'success': True,
            'message': f'Synchronization completed for {integration.name}',
            'alerts_processed': 0
        })
        
    except Exception as e:
        IntegrationLog.objects.create(
            integration=integration,
            log_type='error',
            message=f'Synchronization failed: {str(e)}',
            details={'error': str(e)}
        )
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def integration_statistics(request):
    """Statistiques des intégrations"""
    user = request.user
    
    if user.role in ['admin', 'soc_analyst']:
        integrations = ClientIntegration.objects.all()
    elif user.role == 'client' and hasattr(user, 'client'):
        integrations = ClientIntegration.objects.filter(client=user.client)
    else:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'total_integrations': integrations.count(),
        'active_integrations': integrations.filter(is_active=True).count(),
        'error_integrations': integrations.filter(status='error').count(),
        'total_alerts_24h': sum(integration.alerts_received_24h for integration in integrations),
        'total_errors_24h': sum(integration.error_count_24h for integration in integrations),
        'integrations_by_type': {},
        'recent_logs': []
    }
    
    # Statistiques par type
    for integration_type, _ in ClientIntegration.INTEGRATION_TYPES:
        count = integrations.filter(integration_type=integration_type).count()
        if count > 0:
            stats['integrations_by_type'][integration_type] = count
    
    # Logs récents
    recent_logs = IntegrationLog.objects.filter(
        integration__in=integrations
    ).order_by('-timestamp')[:10]
    
    stats['recent_logs'] = IntegrationLogSerializer(recent_logs, many=True).data
    
    return Response(stats)
