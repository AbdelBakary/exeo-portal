import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone
from .models import ClientIntegration, IntegrationLog

logger = logging.getLogger(__name__)


class ClientAlertMapper:
    """Mapper pour convertir les données clients vers le format EXEO"""
    
    def __init__(self, integration: ClientIntegration):
        self.integration = integration
        self.mapping_config = integration.mapping_config or {}
    
    def map_alert(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mappe les données brutes vers le format Alert EXEO
        
        Args:
            raw_data: Données brutes reçues du système client
            
        Returns:
            Dict mappé pour créer un objet Alert
        """
        try:
            mapped_data = {}
            
            # Mapping des champs obligatoires
            mapped_data['alert_id'] = self._extract_field(raw_data, 'id', 'external_id')
            mapped_data['title'] = self._extract_field(raw_data, 'title', 'event_title', 'summary')
            mapped_data['description'] = self._extract_field(raw_data, 'description', 'message', 'details', default='')
            
            # Mapping de la sévérité avec conversion
            mapped_data['severity'] = self._map_severity(raw_data)
            
            # Mapping du type d'alerte
            mapped_data['alert_type'] = self._extract_field(raw_data, 'alert_type', 'event_type', 'category', default='unknown')
            
            # Mapping des adresses IP
            mapped_data['source_ip'] = self._extract_field(raw_data, 'source_ip', 'src_ip', 'source_address', default='')
            mapped_data['destination_ip'] = self._extract_field(raw_data, 'destination_ip', 'dst_ip', 'destination_address', default='')
            
            # Mapping des ports
            mapped_data['source_port'] = self._extract_field(raw_data, 'source_port', 'src_port', default=None)
            mapped_data['destination_port'] = self._extract_field(raw_data, 'destination_port', 'dst_port', default=None)
            
            # Mapping du protocole
            mapped_data['protocol'] = self._extract_field(raw_data, 'protocol', 'proto', default='')
            
            # Mapping du système source
            mapped_data['source_system'] = self._extract_field(raw_data, 'source_system', 'host', 'device', default=self.integration.name)
            
            # Mapping du timestamp
            mapped_data['detected_at'] = self._map_timestamp(raw_data)
            
            # Mapping des tags
            mapped_data['tags'] = self._extract_field(raw_data, 'tags', 'labels', 'categories', default=[])
            if isinstance(mapped_data['tags'], str):
                mapped_data['tags'] = [mapped_data['tags']]
            
            # Données brutes pour debugging
            mapped_data['raw_data'] = raw_data
            
            # Client (obligatoire) - passer l'ID au lieu de l'objet
            mapped_data['client'] = self.integration.client.id
            
            # Log de l'alerte mappée
            self._log_alert_processed(mapped_data)
            
            return mapped_data
            
        except Exception as e:
            error_msg = f"Erreur de mapping pour l'intégration {self.integration}: {str(e)}"
            logger.error(error_msg)
            self._log_error(error_msg, raw_data)
            raise
    
    def _extract_field(self, data: Dict[str, Any], *field_names: str, default: Any = None) -> Any:
        """Extrait un champ en essayant plusieurs noms possibles"""
        for field_name in field_names:
            if field_name in data:
                return data[field_name]
        
        # Essayer avec des chemins JSON (ex: "event.details.title")
        for field_name in field_names:
            if '.' in field_name:
                try:
                    keys = field_name.split('.')
                    value = data
                    for key in keys:
                        value = value[key]
                    return value
                except (KeyError, TypeError):
                    continue
        
        return default
    
    def _map_severity(self, data: Dict[str, Any]) -> str:
        """Mappe la sévérité vers les valeurs standardisées"""
        severity = self._extract_field(data, 'severity', 'priority', 'level', 'risk', default='medium')
        
        # Mapping des valeurs numériques
        if isinstance(severity, (int, float)):
            if severity <= 1:
                return 'critical'
            elif severity <= 2:
                return 'high'
            elif severity <= 3:
                return 'medium'
            else:
                return 'low'
        
        # Mapping des chaînes
        severity_str = str(severity).lower()
        severity_mapping = {
            '1': 'critical', '2': 'high', '3': 'medium', '4': 'low',
            'critical': 'critical', 'high': 'high', 'medium': 'medium', 'low': 'low',
            'info': 'low', 'warning': 'medium', 'error': 'high', 'fatal': 'critical',
            'urgent': 'critical', 'important': 'high', 'normal': 'medium', 'minor': 'low'
        }
        
        return severity_mapping.get(severity_str, 'medium')
    
    def _map_timestamp(self, data: Dict[str, Any]) -> datetime:
        """Mappe le timestamp vers un objet datetime"""
        timestamp = self._extract_field(data, 'timestamp', 'time', 'created_at', 'detected_at', 'event_time')
        
        if timestamp is None:
            return timezone.now()
        
        # Si c'est déjà un datetime
        if isinstance(timestamp, datetime):
            return timestamp
        
        # Si c'est une chaîne, essayer de la parser
        if isinstance(timestamp, str):
            try:
                # Formats ISO courants
                for fmt in [
                    '%Y-%m-%dT%H:%M:%S.%fZ',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%dT%H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S'
                ]:
                    try:
                        return datetime.strptime(timestamp, fmt)
                    except ValueError:
                        continue
                
                # Parser ISO avec timezone
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Impossible de parser le timestamp: {timestamp}")
                return timezone.now()
        
        # Si c'est un timestamp Unix
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        
        return timezone.now()
    
    def _log_alert_processed(self, mapped_data: Dict[str, Any]):
        """Log une alerte traitée avec succès"""
        IntegrationLog.objects.create(
            integration=self.integration,
            log_type='alert_processed',
            message=f"Alerte mappée: {mapped_data['alert_id']}",
            details={
                'alert_id': mapped_data['alert_id'],
                'severity': mapped_data['severity'],
                'alert_type': mapped_data['alert_type'],
                'source_ip': mapped_data.get('source_ip'),
                'mapped_fields': list(mapped_data.keys())
            }
        )
    
    def _log_error(self, error_message: str, raw_data: Dict[str, Any]):
        """Log une erreur de mapping"""
        IntegrationLog.objects.create(
            integration=self.integration,
            log_type='error',
            message=error_message,
            details={
                'raw_data_keys': list(raw_data.keys()) if raw_data else [],
                'mapping_config': self.mapping_config
            }
        )


class MappingConfigGenerator:
    """Générateur de configurations de mapping pour différents systèmes"""
    
    @staticmethod
    def get_default_mapping(system_type: str) -> Dict[str, Any]:
        """Retourne une configuration de mapping par défaut pour un type de système"""
        
        mappings = {
            'splunk': {
                'id': {'path': 'event_id', 'type': 'string'},
                'title': {'path': 'event_title', 'type': 'string'},
                'description': {'path': 'message', 'type': 'string'},
                'severity': {
                    'path': 'priority',
                    'mapping': {'1': 'critical', '2': 'high', '3': 'medium', '4': 'low'}
                },
                'source_ip': {'path': 'src_ip', 'type': 'ip'},
                'destination_ip': {'path': 'dst_ip', 'type': 'ip'},
                'timestamp': {'path': 'timestamp', 'format': 'iso8601'}
            },
            'qradar': {
                'id': {'path': 'event_id', 'type': 'string'},
                'title': {'path': 'event_name', 'type': 'string'},
                'description': {'path': 'description', 'type': 'string'},
                'severity': {
                    'path': 'severity',
                    'mapping': {'1': 'critical', '2': 'high', '3': 'medium', '4': 'low'}
                },
                'source_ip': {'path': 'sourceip', 'type': 'ip'},
                'destination_ip': {'path': 'destinationip', 'type': 'ip'},
                'timestamp': {'path': 'starttime', 'format': 'iso8601'}
            },
            'fortinet': {
                'id': {'path': 'logid', 'type': 'string'},
                'title': {'path': 'action', 'type': 'string'},
                'description': {'path': 'msg', 'type': 'string'},
                'severity': {
                    'path': 'level',
                    'mapping': {'emergency': 'critical', 'alert': 'high', 'critical': 'high', 'error': 'medium', 'warning': 'medium', 'notice': 'low', 'info': 'low'}
                },
                'source_ip': {'path': 'srcip', 'type': 'ip'},
                'destination_ip': {'path': 'dstip', 'type': 'ip'},
                'timestamp': {'path': 'time', 'format': 'iso8601'}
            },
            'paloalto': {
                'id': {'path': 'serial_number', 'type': 'string'},
                'title': {'path': 'action', 'type': 'string'},
                'description': {'path': 'description', 'type': 'string'},
                'severity': {
                    'path': 'severity',
                    'mapping': {'critical': 'critical', 'high': 'high', 'medium': 'medium', 'low': 'low', 'informational': 'low'}
                },
                'source_ip': {'path': 'src', 'type': 'ip'},
                'destination_ip': {'path': 'dst', 'type': 'ip'},
                'timestamp': {'path': 'receive_time', 'format': 'iso8601'}
            }
        }
        
        return mappings.get(system_type, {})
