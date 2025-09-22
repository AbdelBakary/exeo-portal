"""
Professional Risk Scoring Service based on industry standards.
References: NIST Cybersecurity Framework, MITRE ATT&CK, CVSS, ISO 27001
"""
import logging
from typing import Dict, Tuple, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg
import numpy as np

from .ml_models import risk_scoring_model
from .models import RiskScore, Metric
from apps.alerts.models import Alert
from apps.accounts.models import Client

logger = logging.getLogger(__name__)


class RiskScoringService:
    """
    Professional risk scoring service following industry standards.
    
    Based on:
    - NIST Cybersecurity Framework (NIST CSF)
    - MITRE ATT&CK Framework
    - Common Vulnerability Scoring System (CVSS)
    - ISO 27001 Risk Management
    - Threat Intelligence best practices
    """
    
    # Industry-standard severity weights (NIST/ISO 27001)
    SEVERITY_WEIGHTS = {
        'low': 1.0,
        'medium': 3.0,
        'high': 6.0,
        'critical': 10.0
    }
    
    # Alert type risk multipliers (MITRE ATT&CK based)
    ALERT_TYPE_MULTIPLIERS = {
        'malware': 1.5,
        'phishing': 1.3,
        'intrusion': 1.8,
        'ddos': 1.2,
        'data_exfiltration': 2.0,
        'privilege_escalation': 1.7,
        'lateral_movement': 1.6,
        'persistence': 1.4,
        'command_control': 1.9,
        'exfiltration': 1.8,
        'impact': 1.5,
        'reconnaissance': 0.8,
        'resource_development': 0.9,
        'initial_access': 1.6,
        'execution': 1.3,
        'defense_evasion': 1.4,
        'credential_access': 1.7,
        'discovery': 1.1,
        'collection': 1.2,
        'unknown': 1.0
    }
    
    # Network context risk factors (CVSS inspired)
    NETWORK_RISK_FACTORS = {
        'external_ip': 1.3,      # External IPs are riskier
        'internal_ip': 0.8,      # Internal IPs are less risky
        'private_ip': 0.6,       # Private IPs are least risky
        'known_malicious': 2.0,  # Known malicious IPs
        'suspicious_port': 1.4,  # Suspicious port usage
        'high_risk_port': 1.2,   # High-risk ports (22, 3389, etc.)
        'encrypted_traffic': 0.9 # Encrypted traffic is slightly less risky
    }
    
    def __init__(self):
        self.ml_model = risk_scoring_model
        self.logger = logger
    
    def calculate_alert_risk_score(self, alert: Alert) -> Tuple[float, Dict]:
        """
        Calculate comprehensive risk score for an alert.
        
        Args:
            alert: Alert instance to score
            
        Returns:
            Tuple of (score, factors_dict)
        """
        try:
            # Initialize scoring factors
            factors = {
                'methodology': 'professional_hybrid_v1',
                'calculated_at': timezone.now().isoformat(),
                'components': {}
            }
            
            # 1. Base severity score (NIST/ISO 27001)
            severity_score = self._calculate_severity_score(alert)
            factors['components']['severity'] = {
                'value': severity_score,
                'weight': 0.3,
                'description': 'Base severity from NIST framework'
            }
            
            # 2. Alert type multiplier (MITRE ATT&CK)
            type_multiplier = self._calculate_type_multiplier(alert)
            factors['components']['alert_type'] = {
                'value': type_multiplier,
                'weight': 0.25,
                'description': 'MITRE ATT&CK based type risk'
            }
            
            # 3. Network context analysis (CVSS inspired)
            network_score = self._calculate_network_context(alert)
            factors['components']['network_context'] = {
                'value': network_score,
                'weight': 0.2,
                'description': 'Network context and IP reputation'
            }
            
            # 4. Temporal factors (CVSS temporal metrics)
            temporal_score = self._calculate_temporal_factors(alert)
            factors['components']['temporal'] = {
                'value': temporal_score,
                'weight': 0.15,
                'description': 'Time-based risk factors'
            }
            
            # 5. Client context (Business impact)
            client_score = self._calculate_client_context(alert)
            factors['components']['client_context'] = {
                'value': client_score,
                'weight': 0.1,
                'description': 'Client-specific business impact'
            }
            
            # 6. Machine Learning enhancement
            ml_score = self._calculate_ml_enhancement(alert)
            factors['components']['ml_enhancement'] = {
                'value': ml_score,
                'weight': 0.1,
                'description': 'ML model prediction enhancement'
            }
            
            # Calculate final weighted score
            final_score = (
                severity_score * 0.3 +
                type_multiplier * 0.25 +
                network_score * 0.2 +
                temporal_score * 0.15 +
                client_score * 0.1 +
                ml_score * 0.1
            )
            
            # Apply additional risk factors
            final_score = self._apply_additional_factors(alert, final_score, factors)
            
            # Ensure score is within bounds (0-10)
            final_score = max(0.0, min(10.0, final_score))
            
            # Add confidence and metadata
            factors['confidence'] = self._calculate_confidence(factors)
            factors['risk_level'] = self._get_risk_level(final_score)
            factors['recommendations'] = self._get_recommendations(final_score, factors)
            
            return final_score, factors
            
        except Exception as e:
            self.logger.error(f"Error calculating risk score for alert {alert.id}: {str(e)}")
            # Return default score with error info
            return 5.0, {
                'error': str(e),
                'methodology': 'error_fallback',
                'calculated_at': timezone.now().isoformat()
            }
    
    def _calculate_severity_score(self, alert: Alert) -> float:
        """Calculate base severity score (NIST/ISO 27001)."""
        base_score = self.SEVERITY_WEIGHTS.get(alert.severity, 5.0)
        
        # Adjust based on description keywords
        description = alert.description.lower() if alert.description else ""
        keyword_multipliers = {
            'critical': 1.2,
            'urgent': 1.15,
            'immediate': 1.1,
            'suspicious': 1.05,
            'anomaly': 1.03,
            'normal': 0.9,
            'false positive': 0.3
        }
        
        multiplier = 1.0
        for keyword, mult in keyword_multipliers.items():
            if keyword in description:
                multiplier *= mult
        
        return min(10.0, base_score * multiplier)
    
    def _calculate_type_multiplier(self, alert: Alert) -> float:
        """Calculate alert type risk multiplier (MITRE ATT&CK)."""
        base_multiplier = self.ALERT_TYPE_MULTIPLIERS.get(alert.alert_type, 1.0)
        
        # Adjust based on tags
        if alert.tags:
            tag_multipliers = {
                'apt': 1.5,           # Advanced Persistent Threat
                'ransomware': 1.8,    # Ransomware
                'zero_day': 1.6,      # Zero-day exploit
                'insider': 1.4,       # Insider threat
                'nation_state': 1.7,  # Nation-state actor
                'criminal': 1.3,      # Criminal organization
                'hacktivist': 1.1,    # Hacktivist
                'false_positive': 0.2 # False positive
            }
            
            for tag in alert.tags:
                if isinstance(tag, str) and tag.lower() in tag_multipliers:
                    base_multiplier *= tag_multipliers[tag.lower()]
        
        return min(10.0, base_multiplier)
    
    def _calculate_network_context(self, alert: Alert) -> float:
        """Calculate network context risk (CVSS inspired)."""
        score = 5.0  # Base score
        
        # Source IP analysis
        if alert.source_ip:
            if self._is_external_ip(alert.source_ip):
                score += 1.0
            if self._is_known_malicious_ip(alert.source_ip):
                score += 2.0
        
        # Destination IP analysis
        if alert.destination_ip:
            if self._is_critical_asset(alert.destination_ip):
                score += 1.5
        
        # Port analysis
        if alert.source_port:
            if self._is_suspicious_port(alert.source_port):
                score += 1.0
            if self._is_high_risk_port(alert.source_port):
                score += 0.5
        
        if alert.destination_port:
            if self._is_suspicious_port(alert.destination_port):
                score += 1.0
            if self._is_high_risk_port(alert.destination_port):
                score += 0.5
        
        # Protocol analysis
        if alert.protocol:
            if alert.protocol.lower() in ['tcp', 'udp']:
                score += 0.2
            elif alert.protocol.lower() in ['icmp']:
                score += 0.5
        
        return min(10.0, score)
    
    def _calculate_temporal_factors(self, alert: Alert) -> float:
        """Calculate temporal risk factors (CVSS temporal)."""
        score = 5.0  # Base score
        
        # Ensure detected_at is a datetime object
        if isinstance(alert.detected_at, str):
            from datetime import datetime
            detected_at = datetime.fromisoformat(alert.detected_at.replace('Z', '+00:00'))
        else:
            detected_at = alert.detected_at
        
        # Time of day analysis
        hour = detected_at.hour
        if 2 <= hour <= 6:  # Night time (suspicious)
            score += 1.0
        elif 9 <= hour <= 17:  # Business hours (normal)
            score -= 0.5
        
        # Day of week analysis
        weekday = detected_at.weekday()
        if weekday >= 5:  # Weekend (suspicious)
            score += 0.5
        
        # Frequency analysis (recent alerts from same source)
        recent_time = detected_at - timedelta(hours=24)
        recent_alerts = Alert.objects.filter(
            client=alert.client,
            source_ip=alert.source_ip,
            detected_at__gte=recent_time
        ).count()
        
        if recent_alerts > 5:
            score += 1.0
        elif recent_alerts > 10:
            score += 2.0
        
        return min(10.0, score)
    
    def _calculate_client_context(self, alert: Alert) -> float:
        """Calculate client-specific business impact."""
        score = 5.0  # Base score
        
        # Client criticality (could be enhanced with client metadata)
        if alert.client:
            # Simple heuristic based on client name patterns
            client_name = alert.client.name.lower()
            if any(keyword in client_name for keyword in ['bank', 'financial', 'health', 'government']):
                score += 1.0  # Critical sectors
            elif any(keyword in client_name for keyword in ['retail', 'ecommerce', 'media']):
                score += 0.5  # Important sectors
        
        # Client alert frequency (high frequency = higher risk)
        client_alert_count = Alert.objects.filter(
            client=alert.client,
            detected_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        if client_alert_count > 100:
            score += 1.0
        elif client_alert_count > 500:
            score += 2.0
        
        return min(10.0, score)
    
    def _calculate_ml_enhancement(self, alert: Alert) -> float:
        """Calculate ML model enhancement score."""
        try:
            # Prepare data for ML model
            alert_data = [{
                'severity': alert.severity,
                'alert_type': alert.alert_type,
                'source_ip': alert.source_ip,
                'destination_ip': alert.destination_ip,
                'source_port': alert.source_port,
                'destination_port': alert.destination_port,
                'description': alert.description,
                'tags': alert.tags,
                'raw_data': alert.raw_data,
                'detected_at': alert.detected_at,
                'client_id': alert.client_id
            }]
            
            # Get ML prediction
            ml_scores = self.ml_model.predict(alert_data)
            return float(ml_scores[0]) if ml_scores else 5.0
            
        except Exception as e:
            self.logger.warning(f"ML model prediction failed: {str(e)}")
            return 5.0
    
    def _apply_additional_factors(self, alert: Alert, score: float, factors: Dict) -> float:
        """Apply additional risk factors and adjustments."""
        # Raw data size factor
        if alert.raw_data:
            data_size = len(str(alert.raw_data))
            if data_size > 10000:  # Large data payload
                score += 0.5
                factors['components']['large_payload'] = {
                    'value': 0.5,
                    'description': 'Large data payload detected'
                }
        
        # Tag-based adjustments
        if alert.tags:
            for tag in alert.tags:
                if isinstance(tag, str):
                    tag_lower = tag.lower()
                    if 'anomaly' in tag_lower:
                        score += 0.3
                    elif 'correlation' in tag_lower:
                        score += 0.2
                    elif 'escalation' in tag_lower:
                        score += 0.4
        
        return score
    
    def _calculate_confidence(self, factors: Dict) -> float:
        """Calculate confidence score for the risk assessment."""
        confidence = 0.8  # Base confidence
        
        # Reduce confidence if ML model failed
        if 'ml_enhancement' in factors['components']:
            ml_value = factors['components']['ml_enhancement']['value']
            if ml_value == 5.0:  # Default value indicates ML failure
                confidence -= 0.2
        
        # Increase confidence if multiple factors agree
        component_values = [comp['value'] for comp in factors['components'].values()]
        if len(component_values) > 3:
            variance = np.var(component_values)
            if variance < 2.0:  # Low variance = high agreement
                confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level based on score."""
        if score >= 8.0:
            return 'CRITICAL'
        elif score >= 6.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        elif score >= 2.0:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _get_recommendations(self, score: float, factors: Dict) -> List[str]:
        """Get recommendations based on risk score and factors."""
        recommendations = []
        
        if score >= 8.0:
            recommendations.extend([
                "IMMEDIATE investigation required",
                "Consider incident escalation",
                "Implement emergency containment measures"
            ])
        elif score >= 6.0:
            recommendations.extend([
                "Priority investigation within 4 hours",
                "Review and update security controls",
                "Monitor for related activities"
            ])
        elif score >= 4.0:
            recommendations.extend([
                "Investigate within 24 hours",
                "Review security policies",
                "Consider additional monitoring"
            ])
        else:
            recommendations.extend([
                "Routine investigation",
                "Monitor for patterns",
                "Update threat intelligence"
            ])
        
        return recommendations
    
    # Helper methods for network analysis
    def _is_external_ip(self, ip: str) -> bool:
        """Check if IP is external (simplified)."""
        if not ip:
            return False
        # Simple heuristic - could be enhanced with proper IP range checking
        return not (ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.'))
    
    def _is_known_malicious_ip(self, ip: str) -> bool:
        """Check if IP is known malicious (placeholder)."""
        # This would integrate with threat intelligence feeds
        malicious_ips = [
            '1.1.1.1',  # Example - replace with real threat intel
            '8.8.8.8'   # Example - replace with real threat intel
        ]
        return ip in malicious_ips
    
    def _is_critical_asset(self, ip: str) -> bool:
        """Check if IP is a critical asset (placeholder)."""
        # This would integrate with asset management system
        critical_assets = [
            '192.168.1.1',  # Example - replace with real critical assets
            '192.168.1.10'  # Example - replace with real critical assets
        ]
        return ip in critical_assets
    
    def _is_suspicious_port(self, port: int) -> bool:
        """Check if port is suspicious."""
        suspicious_ports = [23, 135, 139, 445, 1433, 3389, 5432, 6379]
        return port in suspicious_ports
    
    def _is_high_risk_port(self, port: int) -> bool:
        """Check if port is high risk."""
        high_risk_ports = [22, 23, 80, 443, 3389, 5900, 8080]
        return port in high_risk_ports


class ThreatIntelligenceService:
    """
    Service for integrating threat intelligence data.
    """
    
    def __init__(self):
        self.logger = logger
    
    def enrich_alert_with_ti(self, alert: Alert) -> Dict:
        """
        Enrich alert with threat intelligence data.
        
        Args:
            alert: Alert to enrich
            
        Returns:
            Dictionary with threat intelligence data
        """
        ti_data = {
            'ip_reputation': self._check_ip_reputation(alert.source_ip),
            'domain_reputation': self._check_domain_reputation(alert),
            'malware_family': self._identify_malware_family(alert),
            'threat_actor': self._identify_threat_actor(alert),
            'campaign': self._identify_campaign(alert)
        }
        
        return ti_data
    
    def _check_ip_reputation(self, ip: str) -> Dict:
        """Check IP reputation (placeholder for real TI integration)."""
        if not ip:
            return {'status': 'unknown', 'reputation': 'neutral'}
        
        # Placeholder logic - would integrate with VirusTotal, MISP, etc.
        return {
            'status': 'checked',
            'reputation': 'clean',  # or 'malicious', 'suspicious'
            'confidence': 0.8,
            'sources': ['internal_db']
        }
    
    def _check_domain_reputation(self, alert: Alert) -> Dict:
        """Check domain reputation (placeholder)."""
        return {
            'status': 'not_applicable',
            'reputation': 'unknown'
        }
    
    def _identify_malware_family(self, alert: Alert) -> Dict:
        """Identify malware family (placeholder)."""
        return {
            'family': 'unknown',
            'confidence': 0.0
        }
    
    def _identify_threat_actor(self, alert: Alert) -> Dict:
        """Identify threat actor (placeholder)."""
        return {
            'actor': 'unknown',
            'confidence': 0.0
        }
    
    def _identify_campaign(self, alert: Alert) -> Dict:
        """Identify campaign (placeholder)."""
        return {
            'campaign': 'unknown',
            'confidence': 0.0
        }
