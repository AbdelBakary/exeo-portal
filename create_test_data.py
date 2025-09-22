#!/usr/bin/env python
"""
Script to create test data for the EXEO Security Portal
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import Client, User
from apps.alerts.models import Alert
from apps.incidents.models import Incident
from apps.threat_intelligence.models import ThreatIndicator, ThreatSource
from apps.analytics.models import RiskScore

def create_test_data():
    print("Creating test data for EXEO Security Portal...")
    
    # Create clients
    client1, created = Client.objects.get_or_create(
        name="Acme Corporation",
        defaults={
            'contact_email': 'security@acme.com',
            'contact_phone': '+33123456789',
            'address': '123 Business Street, Paris, France',
            'is_active': True
        }
    )
    
    client2, created = Client.objects.get_or_create(
        name="TechStart SAS",
        defaults={
            'contact_email': 'it@techstart.com',
            'contact_phone': '+33987654321',
            'address': '456 Innovation Avenue, Lyon, France',
            'is_active': True
        }
    )
    
    print(f"Created clients: {client1.name}, {client2.name}")
    
    # Create users
    user1, created = User.objects.get_or_create(
        email='client1@acme.com',
        defaults={
            'username': 'client1',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'role': 'client',
            'client': client1,
            'is_active': True
        }
    )
    user1.set_password('password123')
    user1.save()
    
    user2, created = User.objects.get_or_create(
        email='client2@techstart.com',
        defaults={
            'username': 'client2',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'role': 'client',
            'client': client2,
            'is_active': True
        }
    )
    user2.set_password('password123')
    user2.save()
    
    analyst, created = User.objects.get_or_create(
        email='analyst@exeo.com',
        defaults={
            'username': 'analyst',
            'first_name': 'Pierre',
            'last_name': 'Durand',
            'role': 'soc_analyst',
            'is_active': True
        }
    )
    analyst.set_password('password123')
    analyst.save()
    
    print(f"Created users: {user1.email}, {user2.email}, {analyst.email}")
    
    # Create alerts
    alert_types = ['malware', 'phishing', 'ddos', 'intrusion', 'vulnerability']
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['open', 'in_progress', 'closed', 'false_positive']
    
    for i in range(50):
        client = random.choice([client1, client2])
        alert_type = random.choice(alert_types)
        severity = random.choice(severities)
        status = random.choice(statuses)
        
        alert = Alert.objects.create(
            client=client,
            alert_id=f"ALT-{client.id}-{i+1:04d}",
            title=f"Alerte {alert_type.title()} - {i+1}",
            description=f"Description de l'alerte {alert_type} détectée sur le système",
            alert_type=alert_type,
            severity=severity,
            status=status,
            source_ip=f"192.168.1.{random.randint(1, 254)}",
            destination_ip=f"10.0.0.{random.randint(1, 254)}",
            risk_score=round(random.uniform(0, 10), 1),
            detected_at=timezone.now() - timedelta(days=random.randint(0, 30)),
            assigned_to=analyst if random.choice([True, False]) else None
        )
        
        # Create risk score
        RiskScore.objects.create(
            client=alert.client,
            score_type='alert',
            entity_id=str(alert.id),
            entity_type='Alert',
            score=alert.risk_score,
            confidence=round(random.uniform(0.7, 1.0), 2),
            factors={
                'severity': alert.severity,
                'type': alert.alert_type,
                'frequency': random.randint(1, 10),
                'context': 'ml_analysis'
            },
            methodology='ml_model_v1'
        )
    
    print("Created 50 alerts with risk scores")
    
    # Create incidents
    incident_categories = ['malware', 'phishing', 'ddos', 'data_breach', 'insider_threat', 'vulnerability']
    priorities = ['low', 'medium', 'high', 'critical']
    incident_statuses = ['new', 'assigned', 'in_progress', 'resolved', 'closed']
    
    for i in range(20):
        client = random.choice([client1, client2])
        category = random.choice(incident_categories)
        priority = random.choice(priorities)
        status = random.choice(incident_statuses)
        
        incident = Incident.objects.create(
            client=client,
            incident_id=f"INC-{client.id}-{i+1:04d}",
            title=f"Incident {category.title()} - {i+1}",
            description=f"Description de l'incident de sécurité de type {category}",
            category=category,
            priority=priority,
            status=status,
            impact_score=round(random.uniform(0, 10), 1),
            business_impact=f"Impact business pour l'incident {i+1}",
            affected_systems=['Server-01', 'Database-02'],
            affected_users=random.randint(1, 100),
            detected_at=timezone.now() - timedelta(days=random.randint(0, 15)),
            assigned_to=analyst if random.choice([True, False]) else None,
            assigned_by=analyst
        )
    
    print("Created 20 incidents")
    
    # Create threat sources
    threat_sources = ['MISP', 'CERT-FR', 'OSINT', 'Commercial Feed']
    source_types = ['misp', 'cert_fr', 'osint', 'commercial']
    
    sources = []
    for i, (name, source_type) in enumerate(zip(threat_sources, source_types)):
        source, created = ThreatSource.objects.get_or_create(
            name=name,
            defaults={
                'source_type': source_type,
                'description': f'Source de threat intelligence {name}',
                'url': f'https://{name.lower()}.com',
                'is_active': True
            }
        )
        sources.append(source)
    
    # Create threat indicators
    threat_types = ['malware', 'phishing', 'vulnerability', 'ioc']
    indicator_types = ['domain', 'ip', 'hash_md5', 'hash_sha256', 'url']
    confidence_levels = ['low', 'medium', 'high', 'critical']
    
    for i in range(30):
        source = random.choice(sources)
        threat_type = random.choice(threat_types)
        indicator_type = random.choice(indicator_types)
        confidence = random.choice(confidence_levels)
        
        ThreatIndicator.objects.create(
            source=source,
            indicator_type=indicator_type,
            value=f"example{i+1}.com" if indicator_type == 'domain' else f"192.168.1.{i+1}",
            description=f"Description de l'indicateur {indicator_type} pour {threat_type}",
            confidence=confidence,
            threat_type=threat_type,
            malware_family=f"Family-{i+1}" if threat_type == 'malware' else "",
            first_seen=timezone.now() - timedelta(days=random.randint(0, 7)),
            last_seen=timezone.now() - timedelta(hours=random.randint(0, 24)),
            severity_score=round(random.uniform(0, 10), 1),
            is_active=True
        )
    
    print("Created 30 threat intelligence entries")
    
    print("\n✅ Test data created successfully!")
    print("\nTest accounts:")
    print("- Client 1: client1@acme.com / password123")
    print("- Client 2: client2@techstart.com / password123")
    print("- Analyst: analyst@exeo.com / password123")
    print("- Admin: test@test.com / test123 (already exists)")

if __name__ == '__main__':
    create_test_data()
