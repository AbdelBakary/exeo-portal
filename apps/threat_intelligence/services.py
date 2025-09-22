"""
Services for threat intelligence aggregation and processing.
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from .models import (
    ThreatSource, ThreatIndicator, ThreatCampaign, ThreatIntelligenceFeed,
    ThreatCorrelation, ThreatIntelligenceReport
)
from apps.alerts.models import Alert
from apps.accounts.models import Client

logger = logging.getLogger(__name__)


class MISPConnector:
    """Connector for MISP (Malware Information Sharing Platform)."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def get_events(self, days: int = 7) -> List[Dict]:
        """Get recent events from MISP."""
        try:
            since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            url = f"{self.base_url}/events/index"
            params = {
                'since': since,
                'limit': 1000
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching MISP events: {str(e)}")
            return []
    
    def get_event_details(self, event_id: str) -> Optional[Dict]:
        """Get detailed information about a specific event."""
        try:
            url = f"{self.base_url}/events/view/{event_id}"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching MISP event details: {str(e)}")
            return None
    
    def get_indicators(self, event_id: str) -> List[Dict]:
        """Get indicators from a specific event."""
        try:
            url = f"{self.base_url}/attributes/restSearch"
            params = {
                'eventid': event_id,
                'limit': 1000
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('Attribute', [])
            
        except Exception as e:
            logger.error(f"Error fetching MISP indicators: {str(e)}")
            return []


class CERTFRConnector:
    """Connector for CERT-FR (French Computer Emergency Response Team)."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://www.cert.ssi.gouv.fr"
    
    def get_advisories(self, days: int = 7) -> List[Dict]:
        """Get recent security advisories from CERT-FR."""
        try:
            # This is a simplified implementation
            # In reality, you would need to implement the actual CERT-FR API
            url = f"{self.base_url}/advisories"
            params = {
                'days': days,
                'format': 'json'
            }
            
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching CERT-FR advisories: {str(e)}")
            return []
    
    def get_indicators(self, advisory_id: str) -> List[Dict]:
        """Get indicators from a specific advisory."""
        try:
            url = f"{self.base_url}/advisories/{advisory_id}/indicators"
            headers = {}
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error fetching CERT-FR indicators: {str(e)}")
            return []


class OSINTConnector:
    """Connector for Open Source Intelligence feeds."""
    
    def __init__(self):
        self.feeds = [
            {
                'name': 'Abuse.ch',
                'url': 'https://feeds.abuse.ch/urlhaus',
                'type': 'malware_urls'
            },
            {
                'name': 'Malware Domain List',
                'url': 'https://www.malwaredomainlist.com/hostslist/hosts.txt',
                'type': 'malware_domains'
            },
            {
                'name': 'Phishing Database',
                'url': 'https://openphish.com/feed.txt',
                'type': 'phishing_urls'
            }
        ]
    
    def get_indicators(self, feed_type: str = None) -> List[Dict]:
        """Get indicators from OSINT feeds."""
        indicators = []
        
        for feed in self.feeds:
            if feed_type and feed['type'] != feed_type:
                continue
                
            try:
                response = requests.get(feed['url'], timeout=30)
                response.raise_for_status()
                
                # Parse feed based on type
                if feed['type'] == 'malware_urls':
                    indicators.extend(self._parse_urlhaus_feed(response.text, feed['name']))
                elif feed['type'] == 'malware_domains':
                    indicators.extend(self._parse_domain_feed(response.text, feed['name']))
                elif feed['type'] == 'phishing_urls':
                    indicators.extend(self._parse_phishing_feed(response.text, feed['name']))
                    
            except Exception as e:
                logger.error(f"Error fetching {feed['name']}: {str(e)}")
                continue
        
        return indicators
    
    def _parse_urlhaus_feed(self, content: str, source: str) -> List[Dict]:
        """Parse URLhaus feed."""
        indicators = []
        for line in content.strip().split('\n'):
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.split(',')
            if len(parts) >= 2:
                indicators.append({
                    'value': parts[0].strip(),
                    'indicator_type': 'url',
                    'threat_type': 'malware',
                    'description': f"Malware URL from {source}",
                    'source': source,
                    'confidence': 'medium'
                })
        
        return indicators
    
    def _parse_domain_feed(self, content: str, source: str) -> List[Dict]:
        """Parse domain feed."""
        indicators = []
        for line in content.strip().split('\n'):
            if line.startswith('#') or not line.strip():
                continue
            
            domain = line.strip()
            if domain and not domain.startswith('127.0.0.1'):
                indicators.append({
                    'value': domain,
                    'indicator_type': 'domain',
                    'threat_type': 'malware',
                    'description': f"Malware domain from {source}",
                    'source': source,
                    'confidence': 'medium'
                })
        
        return indicators
    
    def _parse_phishing_feed(self, content: str, source: str) -> List[Dict]:
        """Parse phishing feed."""
        indicators = []
        for line in content.strip().split('\n'):
            if line.startswith('#') or not line.strip():
                continue
            
            url = line.strip()
            if url:
                indicators.append({
                    'value': url,
                    'indicator_type': 'url',
                    'threat_type': 'phishing',
                    'description': f"Phishing URL from {source}",
                    'source': source,
                    'confidence': 'high'
                })
        
        return indicators


class ThreatIntelligenceAggregator:
    """Main class for aggregating threat intelligence from multiple sources."""
    
    def __init__(self):
        self.misp_connector = None
        self.certfr_connector = None
        self.osint_connector = OSINTConnector()
        
        # Initialize connectors based on configuration
        if hasattr(settings, 'MISP_URL') and hasattr(settings, 'MISP_API_KEY'):
            self.misp_connector = MISPConnector(settings.MISP_URL, settings.MISP_API_KEY)
        
        if hasattr(settings, 'CERT_FR_API_KEY'):
            self.certfr_connector = CERTFRConnector(settings.CERT_FR_API_KEY)
    
    def aggregate_indicators(self, days: int = 7) -> Dict[str, int]:
        """Aggregate indicators from all sources."""
        results = {
            'misp': 0,
            'certfr': 0,
            'osint': 0,
            'total': 0
        }
        
        # Get MISP indicators
        if self.misp_connector:
            try:
                events = self.misp_connector.get_events(days)
                for event in events:
                    event_id = event.get('Event', {}).get('id')
                    if event_id:
                        indicators = self.misp_connector.get_indicators(event_id)
                        count = self._process_misp_indicators(indicators, event)
                        results['misp'] += count
            except Exception as e:
                logger.error(f"Error processing MISP indicators: {str(e)}")
        
        # Get CERT-FR indicators
        if self.certfr_connector:
            try:
                advisories = self.certfr_connector.get_advisories(days)
                for advisory in advisories:
                    advisory_id = advisory.get('id')
                    if advisory_id:
                        indicators = self.certfr_connector.get_indicators(advisory_id)
                        count = self._process_certfr_indicators(indicators, advisory)
                        results['certfr'] += count
            except Exception as e:
                logger.error(f"Error processing CERT-FR indicators: {str(e)}")
        
        # Get OSINT indicators
        try:
            indicators = self.osint_connector.get_indicators()
            count = self._process_osint_indicators(indicators)
            results['osint'] += count
        except Exception as e:
            logger.error(f"Error processing OSINT indicators: {str(e)}")
        
        results['total'] = sum(results.values())
        return results
    
    def _process_misp_indicators(self, indicators: List[Dict], event: Dict) -> int:
        """Process MISP indicators and save to database."""
        count = 0
        source, _ = ThreatSource.objects.get_or_create(
            name='MISP',
            defaults={
                'source_type': 'misp',
                'description': 'Malware Information Sharing Platform',
                'url': self.misp_connector.base_url
            }
        )
        
        for indicator in indicators:
            try:
                with transaction.atomic():
                    threat_indicator, created = ThreatIndicator.objects.get_or_create(
                        source=source,
                        indicator_type=indicator.get('type', 'other'),
                        value=indicator.get('value', ''),
                        defaults={
                            'description': indicator.get('comment', ''),
                            'confidence': self._map_confidence(indicator.get('to_ids', False)),
                            'threat_type': self._extract_threat_type(event),
                            'malware_family': self._extract_malware_family(event),
                            'actor': self._extract_actor(event),
                            'first_seen': datetime.fromisoformat(
                                indicator.get('timestamp', datetime.now().isoformat())
                            ),
                            'tags': indicator.get('Tag', []),
                            'references': [indicator.get('uuid', '')],
                            'severity_score': self._calculate_severity_score(indicator, event)
                        }
                    )
                    
                    if created:
                        count += 1
                        
            except Exception as e:
                logger.error(f"Error processing MISP indicator: {str(e)}")
                continue
        
        return count
    
    def _process_certfr_indicators(self, indicators: List[Dict], advisory: Dict) -> int:
        """Process CERT-FR indicators and save to database."""
        count = 0
        source, _ = ThreatSource.objects.get_or_create(
            name='CERT-FR',
            defaults={
                'source_type': 'cert_fr',
                'description': 'French Computer Emergency Response Team',
                'url': 'https://www.cert.ssi.gouv.fr'
            }
        )
        
        for indicator in indicators:
            try:
                with transaction.atomic():
                    threat_indicator, created = ThreatIndicator.objects.get_or_create(
                        source=source,
                        indicator_type=indicator.get('type', 'other'),
                        value=indicator.get('value', ''),
                        defaults={
                            'description': indicator.get('description', ''),
                            'confidence': 'high',  # CERT-FR is authoritative
                            'threat_type': advisory.get('category', 'unknown'),
                            'first_seen': datetime.fromisoformat(
                                indicator.get('created', datetime.now().isoformat())
                            ),
                            'severity_score': self._calculate_certfr_severity(advisory)
                        }
                    )
                    
                    if created:
                        count += 1
                        
            except Exception as e:
                logger.error(f"Error processing CERT-FR indicator: {str(e)}")
                continue
        
        return count
    
    def _process_osint_indicators(self, indicators: List[Dict]) -> int:
        """Process OSINT indicators and save to database."""
        count = 0
        
        for indicator in indicators:
            try:
                source, _ = ThreatSource.objects.get_or_create(
                    name=indicator.get('source', 'OSINT'),
                    defaults={
                        'source_type': 'osint',
                        'description': f"Open Source Intelligence - {indicator.get('source', 'OSINT')}"
                    }
                )
                
                with transaction.atomic():
                    threat_indicator, created = ThreatIndicator.objects.get_or_create(
                        source=source,
                        indicator_type=indicator.get('indicator_type', 'other'),
                        value=indicator.get('value', ''),
                        defaults={
                            'description': indicator.get('description', ''),
                            'confidence': indicator.get('confidence', 'medium'),
                            'threat_type': indicator.get('threat_type', 'unknown'),
                            'first_seen': datetime.now(),
                            'severity_score': self._calculate_osint_severity(indicator)
                        }
                    )
                    
                    if created:
                        count += 1
                        
            except Exception as e:
                logger.error(f"Error processing OSINT indicator: {str(e)}")
                continue
        
        return count
    
    def correlate_with_alerts(self, client: Client = None) -> Dict[str, int]:
        """Correlate threat indicators with existing alerts."""
        correlations = {
            'ip_matches': 0,
            'domain_matches': 0,
            'url_matches': 0,
            'hash_matches': 0,
            'total': 0
        }
        
        # Get active threat indicators
        indicators = ThreatIndicator.objects.filter(is_active=True)
        if client:
            # Filter by client-specific indicators if needed
            pass
        
        # Get alerts to correlate
        alerts = Alert.objects.filter(status__in=['open', 'in_progress'])
        if client:
            alerts = alerts.filter(client=client)
        
        for alert in alerts:
            for indicator in indicators:
                try:
                    correlation_type = None
                    matched_value = None
                    
                    # Check IP matches
                    if (indicator.indicator_type == 'ip' and 
                        indicator.value in [alert.source_ip, alert.destination_ip]):
                        correlation_type = 'ip_match'
                        matched_value = indicator.value
                    
                    # Check domain matches
                    elif (indicator.indicator_type == 'domain' and 
                          alert.description and indicator.value.lower() in alert.description.lower()):
                        correlation_type = 'domain_match'
                        matched_value = indicator.value
                    
                    # Check URL matches
                    elif (indicator.indicator_type == 'url' and 
                          alert.description and indicator.value in alert.description):
                        correlation_type = 'url_match'
                        matched_value = indicator.value
                    
                    # Check hash matches
                    elif (indicator.indicator_type in ['hash_md5', 'hash_sha1', 'hash_sha256'] and 
                          alert.raw_data and indicator.value in str(alert.raw_data)):
                        correlation_type = 'hash_match'
                        matched_value = indicator.value
                    
                    if correlation_type:
                        # Create correlation
                        ThreatCorrelation.objects.get_or_create(
                            client=alert.client,
                            threat_indicator=indicator,
                            correlation_type=correlation_type,
                            matched_value=matched_value,
                            defaults={
                                'confidence_score': 0.8,
                                'context': {
                                    'alert_id': alert.alert_id,
                                    'alert_title': alert.title,
                                    'correlated_at': timezone.now().isoformat()
                                }
                            }
                        )
                        
                        correlations[f'{correlation_type}s'] += 1
                        correlations['total'] += 1
                        
                except Exception as e:
                    logger.error(f"Error correlating indicator {indicator.id} with alert {alert.id}: {str(e)}")
                    continue
        
        return correlations
    
    def _map_confidence(self, to_ids: bool) -> str:
        """Map MISP to_ids field to confidence level."""
        return 'high' if to_ids else 'medium'
    
    def _extract_threat_type(self, event: Dict) -> str:
        """Extract threat type from MISP event."""
        event_data = event.get('Event', {})
        tags = event_data.get('Tag', [])
        
        for tag in tags:
            tag_name = tag.get('name', '').lower()
            if 'apt' in tag_name:
                return 'apt'
            elif 'malware' in tag_name:
                return 'malware'
            elif 'phishing' in tag_name:
                return 'phishing'
            elif 'ddos' in tag_name:
                return 'ddos'
        
        return 'unknown'
    
    def _extract_malware_family(self, event: Dict) -> str:
        """Extract malware family from MISP event."""
        event_data = event.get('Event', {})
        tags = event_data.get('Tag', [])
        
        for tag in tags:
            tag_name = tag.get('name', '')
            if 'malware' in tag_name.lower():
                return tag_name.replace('malware:', '').replace('Malware:', '')
        
        return ''
    
    def _extract_actor(self, event: Dict) -> str:
        """Extract threat actor from MISP event."""
        event_data = event.get('Event', {})
        tags = event_data.get('Tag', [])
        
        for tag in tags:
            tag_name = tag.get('name', '')
            if 'actor' in tag_name.lower():
                return tag_name.replace('actor:', '').replace('Actor:', '')
        
        return ''
    
    def _calculate_severity_score(self, indicator: Dict, event: Dict) -> float:
        """Calculate severity score for MISP indicator."""
        score = 5.0  # Base score
        
        # Adjust based on confidence
        if indicator.get('to_ids'):
            score += 2.0
        
        # Adjust based on event threat level
        event_data = event.get('Event', {})
        threat_level = event_data.get('threat_level_id', 1)
        score += threat_level * 0.5
        
        return min(score, 10.0)
    
    def _calculate_certfr_severity(self, advisory: Dict) -> float:
        """Calculate severity score for CERT-FR advisory."""
        score = 6.0  # Base score for CERT-FR
        
        # Adjust based on advisory severity
        severity = advisory.get('severity', 'medium')
        if severity == 'high':
            score += 2.0
        elif severity == 'critical':
            score += 3.0
        
        return min(score, 10.0)
    
    def _calculate_osint_severity(self, indicator: Dict) -> float:
        """Calculate severity score for OSINT indicator."""
        score = 4.0  # Base score for OSINT
        
        # Adjust based on confidence
        confidence = indicator.get('confidence', 'medium')
        if confidence == 'high':
            score += 2.0
        elif confidence == 'critical':
            score += 3.0
        
        # Adjust based on threat type
        threat_type = indicator.get('threat_type', 'unknown')
        if threat_type in ['apt', 'malware']:
            score += 1.0
        
        return min(score, 10.0)


# Global aggregator instance
threat_intelligence_aggregator = ThreatIntelligenceAggregator()
