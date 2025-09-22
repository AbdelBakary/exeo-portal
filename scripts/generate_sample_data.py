#!/usr/bin/env python
"""
Script to generate sample data for the EXEO Portal.
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import Client, User
from apps.alerts.models import Alert, AlertComment, AlertRule
from apps.incidents.models import Incident, IncidentComment
from apps.threat_intelligence.models import ThreatSource, ThreatIndicator, ThreatCampaign
from apps.analytics.models import RiskScore, Metric
from apps.soar.models import Playbook, Action, Integration

def generate_sample_data():
    """Generate comprehensive sample data for testing."""
    
    print("Generating sample data...")
    
    # Get or create clients
    clients = []
    for i in range(3):
        client, created = Client.objects.get_or_create(
            name=f'Client {i+1}',
            defaults={
                'contact_email': f'contact{i+1}@client.com',
                'contact_phone': f'+33 1 23 45 67 8{i}',
                'address': f'{100+i} Rue de la Sécurité, 7500{i+1} Paris, France',
                'timezone': 'Europe/Paris',
                'is_active': True
            }
        )
        clients.append(client)
        if created:
            print(f"Created client: {client.name}")
    
    # Get or create users
    users = []
    for client in clients:
        for role in ['soc_analyst', 'client']:
            user, created = User.objects.get_or_create(
                email=f'{role}@{client.name.lower().replace(" ", "")}.com',
                defaults={
                    'username': f'{role}_{client.name.lower().replace(" ", "")}',
                    'first_name': f'{role.title()}',
                    'last_name': client.name,
                    'role': role,
                    'client': client,
                    'is_verified': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
    
    # Create threat sources
    threat_sources = []
    source_data = [
        {'name': 'MISP', 'source_type': 'misp', 'description': 'Malware Information Sharing Platform'},
        {'name': 'CERT-FR', 'source_type': 'cert_fr', 'description': 'French Computer Emergency Response Team'},
        {'name': 'Abuse.ch', 'source_type': 'osint', 'description': 'Open Source Intelligence Feed'},
        {'name': 'VirusTotal', 'source_type': 'commercial', 'description': 'Commercial Threat Intelligence'},
    ]
    
    for source_info in source_data:
        source, created = ThreatSource.objects.get_or_create(
            name=source_info['name'],
            defaults=source_info
        )
        threat_sources.append(source)
        if created:
            print(f"Created threat source: {source.name}")
    
    # Create threat indicators
    indicator_types = ['ip', 'domain', 'url', 'hash_md5', 'hash_sha256', 'email']
    threat_types = ['malware', 'phishing', 'apt', 'ddos', 'botnet']
    confidence_levels = ['low', 'medium', 'high', 'critical']
    
    for i in range(100):
        indicator, created = ThreatIndicator.objects.get_or_create(
            source=random.choice(threat_sources),
            indicator_type=random.choice(indicator_types),
            value=f'sample_{i}_{random.randint(1000, 9999)}',
            defaults={
                'description': f'Sample threat indicator {i}',
                'confidence': random.choice(confidence_levels),
                'threat_type': random.choice(threat_types),
                'malware_family': f'Malware_{i}' if random.random() > 0.7 else '',
                'first_seen': datetime.now() - timedelta(days=random.randint(1, 30)),
                'severity_score': random.uniform(1.0, 10.0),
                'is_active': random.random() > 0.1,
            }
        )
        if created:
            print(f"Created threat indicator: {indicator.value}")
    
    # Create alerts
    alert_types = ['malware', 'phishing', 'ddos', 'intrusion', 'data_exfiltration', 'suspicious_activity']
    severity_levels = ['low', 'medium', 'high', 'critical']
    status_choices = ['open', 'in_progress', 'closed', 'false_positive']
    
    for i in range(200):
        client = random.choice(clients)
        alert, created = Alert.objects.get_or_create(
            alert_id=f'ALERT-{i+1:06d}',
            defaults={
                'client': client,
                'title': f'Sample Alert {i+1}',
                'description': f'This is a sample security alert for testing purposes. Alert number {i+1}.',
                'alert_type': random.choice(alert_types),
                'severity': random.choice(severity_levels),
                'status': random.choice(status_choices),
                'source_ip': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'destination_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'source_port': random.randint(1, 65535),
                'destination_port': random.randint(1, 65535),
                'protocol': random.choice(['TCP', 'UDP', 'ICMP']),
                'source_system': random.choice(['SIEM', 'Firewall', 'IDS', 'EDR']),
                'detected_at': datetime.now() - timedelta(days=random.randint(0, 30)),
                'risk_score': random.uniform(0.0, 10.0),
                'assigned_to': random.choice(users) if random.random() > 0.3 else None,
            }
        )
        if created:
            print(f"Created alert: {alert.alert_id}")
    
    # Create incidents
    incident_categories = ['malware', 'phishing', 'ddos', 'data_breach', 'insider_threat', 'vulnerability']
    priority_levels = ['low', 'medium', 'high', 'critical']
    incident_statuses = ['new', 'assigned', 'in_progress', 'resolved', 'closed']
    
    for i in range(50):
        client = random.choice(clients)
        incident, created = Incident.objects.get_or_create(
            incident_id=f'INC-{i+1:04d}',
            defaults={
                'client': client,
                'title': f'Sample Incident {i+1}',
                'description': f'This is a sample security incident for testing purposes. Incident number {i+1}.',
                'category': random.choice(incident_categories),
                'priority': random.choice(priority_levels),
                'status': random.choice(incident_statuses),
                'detected_at': datetime.now() - timedelta(days=random.randint(0, 30)),
                'reported_at': datetime.now() - timedelta(days=random.randint(0, 30)),
                'impact_score': random.uniform(0.0, 10.0),
                'assigned_to': random.choice(users) if random.random() > 0.4 else None,
            }
        )
        if created:
            print(f"Created incident: {incident.incident_id}")
    
    # Create risk scores
    alerts = Alert.objects.all()[:50]
    for alert in alerts:
        risk_score, created = RiskScore.objects.get_or_create(
            client=alert.client,
            score_type='alert',
            entity_id=str(alert.id),
            defaults={
                'entity_type': 'Alert',
                'score': alert.risk_score,
                'confidence': random.uniform(0.5, 1.0),
                'factors': {
                    'severity': alert.severity,
                    'type': alert.alert_type,
                    'ml_model': 'gradient_boosting_v1'
                },
                'methodology': 'ml_model_v1'
            }
        )
        if created:
            print(f"Created risk score for alert {alert.id}")
    
    # Create metrics
    for client in clients:
        for metric_name in ['total_alerts', 'open_alerts', 'avg_risk_score', 'alerts_24h']:
            metric, created = Metric.objects.get_or_create(
                client=client,
                name=metric_name,
                period_start=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                period_end=datetime.now(),
                defaults={
                    'metric_type': 'count' if 'alerts' in metric_name else 'average',
                    'value': random.randint(10, 100) if 'alerts' in metric_name else random.uniform(1.0, 10.0),
                    'unit': 'count' if 'alerts' in metric_name else 'score',
                    'calculation_method': 'direct'
                }
            )
            if created:
                print(f"Created metric {metric_name} for {client.name}")
    
    # Create SOAR playbooks
    for i in range(5):
        playbook, created = Playbook.objects.get_or_create(
            name=f'Sample Playbook {i+1}',
            defaults={
                'client': random.choice(clients),
                'description': f'This is a sample SOAR playbook for testing purposes.',
                'trigger_type': 'alert_created',
                'trigger_conditions': {
                    'severity': ['high', 'critical'],
                    'alert_type': ['malware', 'phishing']
                },
                'steps': [
                    {
                        'name': 'Send Notification',
                        'action_type': 'email_notification',
                        'parameters': {
                            'recipients': ['analyst@exeo.com'],
                            'subject': 'High Priority Alert: ${alert_title}',
                            'template': 'soar/alert_notification.html'
                        }
                    },
                    {
                        'name': 'Assign Alert',
                        'action_type': 'assign_alert',
                        'parameters': {
                            'user_id': '${assigned_user_id}'
                        }
                    }
                ],
                'is_enabled': random.random() > 0.2,
                'created_by': random.choice(users)
            }
        )
        if created:
            print(f"Created playbook: {playbook.name}")
    
    print("Sample data generation completed!")

if __name__ == '__main__':
    generate_sample_data()
