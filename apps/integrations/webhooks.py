import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import ClientIntegration, IntegrationLog
from .mappers import ClientAlertMapper
from .serializers import WebhookAlertSerializer
from apps.alerts.models import Alert
from apps.alerts.serializers import AlertCreateSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def client_webhook(request):
    """
    Webhook universel pour recevoir les alertes des clients
    
    Headers requis:
    - X-Client-Token: Token d'authentification du client
    
    Body JSON:
    {
        "external_id": "ALERT-123",
        "title": "Suspicious activity detected",
        "description": "Multiple failed login attempts",
        "severity": "high",
        "alert_type": "intrusion",
        "source_ip": "192.168.1.100",
        "destination_ip": "10.0.0.1",
        "timestamp": "2024-01-01T10:00:00Z",
        "raw_data": {...}
    }
    """
    try:
        # Récupération du token client
        client_token = request.headers.get('X-Client-Token')
        if not client_token:
            return Response(
                {'error': 'X-Client-Token header required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Recherche de l'intégration correspondante
        try:
            integration = ClientIntegration.objects.get(
                api_token=client_token,
                is_active=True
            )
        except ClientIntegration.DoesNotExist:
            return Response(
                {'error': 'Invalid or inactive client token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Validation du JSON reçu
        try:
            raw_data = request.data
        except Exception as e:
            return Response(
                {'error': f'Invalid JSON: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log de l'alerte reçue
        IntegrationLog.objects.create(
            integration=integration,
            log_type='alert_received',
            message=f"Alerte reçue: {raw_data.get('external_id', 'unknown')}",
            details={'raw_data_keys': list(raw_data.keys())}
        )
        
        # Mapping des données
        try:
            mapper = ClientAlertMapper(integration)
            mapped_data = mapper.map_alert(raw_data)
        except Exception as e:
            logger.error(f"Erreur de mapping pour l'intégration {integration}: {str(e)}")
            integration.increment_error_count()
            return Response(
                {'error': f'Mapping error: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Création de l'alerte
        try:
            # Utiliser le serializer existant pour créer l'alerte
            alert_serializer = AlertCreateSerializer(data=mapped_data)
            if alert_serializer.is_valid():
                alert = alert_serializer.save()
                
                # Mise à jour des statistiques
                integration.increment_alert_count()
                integration.update_sync_status(success=True)
                
                # Log de succès
                IntegrationLog.objects.create(
                    integration=integration,
                    log_type='alert_processed',
                    message=f"Alerte créée avec succès: {alert.alert_id}",
                    details={
                        'alert_id': alert.alert_id,
                        'risk_score': alert.risk_score,
                        'severity': alert.severity
                    }
                )
                
                return Response({
                    'success': True,
                    'alert_id': alert.alert_id,
                    'risk_score': alert.risk_score,
                    'message': 'Alert created successfully'
                }, status=status.HTTP_201_CREATED)
            else:
                error_msg = f"Validation error: {alert_serializer.errors}"
                logger.error(error_msg)
                integration.increment_error_count()
                return Response(
                    {'error': error_msg}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            error_msg = f"Error creating alert: {str(e)}"
            logger.error(error_msg)
            integration.increment_error_count()
            integration.update_sync_status(success=False, error_message=error_msg)
            return Response(
                {'error': error_msg}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def webhook_status(request):
    """Endpoint de statut pour vérifier la santé du webhook"""
    return Response({
        'status': 'healthy',
        'message': 'Webhook is operational',
        'timestamp': timezone.now().isoformat()
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def test_webhook(request):
    """
    Endpoint de test pour valider la configuration du webhook
    """
    try:
        client_token = request.headers.get('X-Client-Token')
        if not client_token:
            return Response(
                {'error': 'X-Client-Token header required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            integration = ClientIntegration.objects.get(api_token=client_token)
        except ClientIntegration.DoesNotExist:
            return Response(
                {'error': 'Invalid client token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Test de mapping avec des données d'exemple
        test_data = {
            'external_id': 'TEST-123',
            'title': 'Test Alert',
            'description': 'This is a test alert',
            'severity': 'medium',
            'alert_type': 'test',
            'timestamp': timezone.now().isoformat()
        }
        
        mapper = ClientAlertMapper(integration)
        mapped_data = mapper.map_alert(test_data)
        
        return Response({
            'success': True,
            'message': 'Webhook configuration is valid',
            'integration': {
                'name': integration.name,
                'type': integration.integration_type,
                'client': integration.client.name
            },
            'mapped_data': mapped_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Test failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
