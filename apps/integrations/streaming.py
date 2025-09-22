import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import IntegrationLog

logger = logging.getLogger(__name__)


class AlertStreamingConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket pour le streaming des alertes en temps réel"""
    
    async def connect(self):
        """Connexion WebSocket"""
        self.room_group_name = 'alerts_stream'
        
        # Rejoindre le groupe
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Log de connexion
        await self.log_connection('connected')
        
        logger.info(f"WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Log de déconnexion
        await self.log_connection('disconnected')
        
        logger.info(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")
    
    async def receive(self, text_data):
        """Réception de messages du client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': self.get_timestamp()
                }))
            elif message_type == 'subscribe':
                # Le client peut s'abonner à des types d'alertes spécifiques
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'message': 'Successfully subscribed to alerts'
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unknown message type'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in WebSocket receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal error'
            }))
    
    async def alert_notification(self, event):
        """Envoi d'une notification d'alerte au client"""
        try:
            # Préparer les données de l'alerte
            alert_data = {
                'type': 'alert',
                'alert_id': event['alert_id'],
                'client': event['client'],
                'severity': event['severity'],
                'risk_score': event['risk_score'],
                'title': event['title'],
                'alert_type': event['alert_type'],
                'timestamp': event['timestamp'],
                'source_ip': event.get('source_ip', ''),
                'destination_ip': event.get('destination_ip', ''),
            }
            
            # Envoyer au client
            await self.send(text_data=json.dumps(alert_data))
            
            # Log de l'envoi
            await self.log_alert_sent(event['alert_id'])
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {str(e)}")
    
    async def integration_status_update(self, event):
        """Envoi d'une mise à jour de statut d'intégration"""
        try:
            status_data = {
                'type': 'integration_status',
                'integration_id': event['integration_id'],
                'integration_name': event['integration_name'],
                'client': event['client'],
                'status': event['status'],
                'message': event['message'],
                'timestamp': event['timestamp']
            }
            
            await self.send(text_data=json.dumps(status_data))
            
        except Exception as e:
            logger.error(f"Error sending integration status update: {str(e)}")
    
    async def log_connection(self, action):
        """Log de connexion/déconnexion"""
        try:
            await database_sync_to_async(IntegrationLog.objects.create)(
                integration=None,  # Pas d'intégration spécifique pour les connexions WebSocket
                log_type='connection_test',
                message=f"WebSocket {action}",
                details={'channel_name': self.channel_name}
            )
        except Exception as e:
            logger.error(f"Error logging connection: {str(e)}")
    
    async def log_alert_sent(self, alert_id):
        """Log d'envoi d'alerte"""
        try:
            await database_sync_to_async(IntegrationLog.objects.create)(
                integration=None,
                log_type='alert_processed',
                message=f"Alert {alert_id} sent via WebSocket",
                details={'alert_id': alert_id, 'channel_name': self.channel_name}
            )
        except Exception as e:
            logger.error(f"Error logging alert sent: {str(e)}")
    
    def get_timestamp(self):
        """Retourne le timestamp actuel"""
        from django.utils import timezone
        return timezone.now().isoformat()


class AlertStreamingService:
    """Service pour publier des alertes via WebSocket"""
    
    def __init__(self):
        from channels.layers import get_channel_layer
        self.channel_layer = get_channel_layer()
        self.room_group_name = 'alerts_stream'
    
    async def publish_alert(self, alert):
        """Publie une alerte via WebSocket"""
        try:
            alert_data = {
                'type': 'alert_notification',
                'alert_id': alert.alert_id,
                'client': alert.client.name,
                'severity': alert.severity,
                'risk_score': alert.risk_score,
                'title': alert.title,
                'alert_type': alert.alert_type,
                'timestamp': alert.detected_at.isoformat(),
                'source_ip': alert.source_ip or '',
                'destination_ip': alert.destination_ip or '',
            }
            
            await self.channel_layer.group_send(
                self.room_group_name,
                alert_data
            )
            
            logger.info(f"Alert {alert.alert_id} published via WebSocket")
            
        except Exception as e:
            logger.error(f"Error publishing alert via WebSocket: {str(e)}")
    
    async def publish_integration_status(self, integration, status, message):
        """Publie une mise à jour de statut d'intégration"""
        try:
            status_data = {
                'type': 'integration_status_update',
                'integration_id': str(integration.id),
                'integration_name': integration.name,
                'client': integration.client.name,
                'status': status,
                'message': message,
                'timestamp': self.get_timestamp()
            }
            
            await self.channel_layer.group_send(
                self.room_group_name,
                status_data
            )
            
            logger.info(f"Integration status update published: {integration.name}")
            
        except Exception as e:
            logger.error(f"Error publishing integration status: {str(e)}")
    
    def get_timestamp(self):
        """Retourne le timestamp actuel"""
        from django.utils import timezone
        return timezone.now().isoformat()


# Instance globale du service
alert_streaming_service = AlertStreamingService()
