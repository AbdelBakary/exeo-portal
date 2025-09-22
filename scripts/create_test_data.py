#!/usr/bin/env python
"""
Script to create test data for EXEO Security Portal.
This creates clients, users, and alerts for testing the multi-tenant system.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import Client, User
from apps.alerts.models import Alert
from apps.incidents.models import Incident

def create_test_clients():
    """Create test clients."""
    clients_data = [
        {
            'name': 'Entreprise Alpha',
            'contact_email': 'contact@alpha.com',
            'contact_phone': '+33123456789',
            'address': '123 Rue de la Paix, 75001 Paris',
            'timezone': 'Europe/Paris'
        },
        {
            'name': 'Société Beta',
            'contact_email': 'admin@beta.com',
            'contact_phone': '+33987654321',
            'address': '456 Avenue des Champs, 75008 Paris',
            'timezone': 'Europe/Paris'
        },
        {
            'name': 'Corporation Gamma',
            'contact_email': 'security@gamma.com',
            'contact_phone': '+33555666777',
            'address': '789 Boulevard Saint-Germain, 75006 Paris',
            'timezone': 'Europe/Paris'
        }
    ]
    
    clients = []
    for client_data in clients_data:
        client, created = Client.objects.get_or_create(
            name=client_data['name'],
            defaults=client_data
        )
        clients.append(client)
        print(f"Client {'created' if created else 'already exists'}: {client.name}")
    
    return clients

def create_test_users(clients):
    """Create test users for each client."""
    users_data = [
        # Admin users
        {
            'username': 'admin_exeo',
            'email': 'admin@exeo.com',
            'first_name': 'Admin',
            'last_name': 'EXEO',
            'role': 'admin',
            'client': None,
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'soc_analyst_exeo',
            'email': 'analyst@exeo.com',
            'first_name': 'Analyste',
            'last_name': 'SOC',
            'role': 'soc_analyst',
            'client': None,
            'is_staff': True
        }
    ]
    
    # Client users
    for i, client in enumerate(clients):
        users_data.extend([
            {
                'username': f'client_{client.name.lower().replace(" ", "_")}',
                'email': f'user1@{client.name.lower().replace(" ", "")}.com',
                'first_name': f'User{i+1}',
                'last_name': client.name.split()[0],
                'role': 'client',
                'client': client
            },
            {
                'username': f'manager_{client.name.lower().replace(" ", "_")}',
                'email': f'manager@{client.name.lower().replace(" ", "")}.com',
                'first_name': f'Manager{i+1}',
                'last_name': client.name.split()[0],
                'role': 'client',
                'client': client
            }
        ])
    
    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
        print(f"User {'created' if created else 'already exists'}: {user.email} ({user.role})")
    
    return users

def create_test_alerts(clients):
    """Create test alerts for each client."""
    alert_types = ['malware', 'phishing', 'ddos', 'intrusion', 'suspicious_activity', 'vulnerability']
    severities = ['low', 'medium', 'high', 'critical']
    statuses = ['open', 'in_progress', 'closed', 'false_positive']
    
    alerts = []
    for client in clients:
        # Create 5-10 alerts per client
        num_alerts = random.randint(5, 10)
        
        for i in range(num_alerts):
            # Random dates in the last 30 days
            detected_at = datetime.now() - timedelta(days=random.randint(0, 30))
            
            alert_data = {
                'client': client,
                'alert_id': f'ALERT-{client.name.upper()}-{i+1:03d}',
                'title': f'Alerte de sécurité {i+1} - {random.choice(alert_types).title()}',
                'description': f'Description de l\'alerte de sécurité détectée le {detected_at.strftime("%d/%m/%Y")}',
                'alert_type': random.choice(alert_types),
                'severity': random.choice(severities),
                'status': random.choice(statuses),
                'source_ip': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'destination_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'source_port': random.randint(1024, 65535),
                'destination_port': random.choice([80, 443, 22, 21, 25, 53]),
                'protocol': random.choice(['TCP', 'UDP', 'ICMP']),
                'source_system': random.choice(['SIEM', 'Firewall', 'IDS', 'Antivirus']),
                'detected_at': detected_at,
                'risk_score': round(random.uniform(0, 10), 1),
                'raw_data': {
                    'source': 'test_data',
                    'timestamp': detected_at.isoformat(),
                    'additional_info': f'Test alert {i+1} for {client.name}'
                },
                'tags': [random.choice(['urgent', 'review', 'escalated', 'resolved'])]
            }
            
            alert, created = Alert.objects.get_or_create(
                alert_id=alert_data['alert_id'],
                defaults=alert_data
            )
            alerts.append(alert)
            print(f"Alert {'created' if created else 'already exists'}: {alert.alert_id} for {client.name}")
    
    return alerts

def create_test_incidents(clients, alerts):
    """Create test incidents linked to alerts."""
    priorities = ['low', 'medium', 'high', 'critical']
    categories = ['malware', 'phishing', 'ddos', 'data_breach', 'vulnerability']
    statuses = ['new', 'assigned', 'in_progress', 'resolved', 'closed']
    
    incidents = []
    for client in clients:
        # Create 2-5 incidents per client
        num_incidents = random.randint(2, 5)
        client_alerts = [a for a in alerts if a.client == client]
        
        for i in range(num_incidents):
            reported_at = datetime.now() - timedelta(days=random.randint(0, 15))
            
            incident_data = {
                'client': client,
                'incident_id': f'INC-{client.name.upper()}-{i+1:03d}',
                'title': f'Incident de sécurité {i+1} - {random.choice(categories).title()}',
                'description': f'Description de l\'incident de sécurité signalé le {reported_at.strftime("%d/%m/%Y")}',
                'category': random.choice(categories),
                'priority': random.choice(priorities),
                'status': random.choice(statuses),
                'impact_score': round(random.uniform(0, 10), 1),
                'business_impact': f'Impact business pour {client.name}',
                'affected_systems': [f'system-{j}' for j in range(random.randint(1, 3))],
                'affected_users': random.randint(1, 100),
                'detected_at': reported_at,
                'reported_at': reported_at,
                'tags': [random.choice(['urgent', 'escalated', 'resolved', 'investigation'])]
            }
            
            incident, created = Incident.objects.get_or_create(
                incident_id=incident_data['incident_id'],
                defaults=incident_data
            )
            
            # Link some alerts to this incident
            if client_alerts:
                related_alerts = random.sample(client_alerts, min(2, len(client_alerts)))
                incident.related_alerts.set(related_alerts)
            
            incidents.append(incident)
            print(f"Incident {'created' if created else 'already exists'}: {incident.incident_id} for {client.name}")
    
    return incidents

def main():
    """Main function to create all test data."""
    print("Creating test data for EXEO Security Portal...")
    print("=" * 50)
    
    # Create clients
    print("\n1. Creating clients...")
    clients = create_test_clients()
    
    # Create users
    print("\n2. Creating users...")
    users = create_test_users(clients)
    
    # Create alerts
    print("\n3. Creating alerts...")
    alerts = create_test_alerts(clients)
    
    # Create incidents
    print("\n4. Creating incidents...")
    incidents = create_test_incidents(clients, alerts)
    
    print("\n" + "=" * 50)
    print("Test data creation completed!")
    print(f"- {len(clients)} clients created")
    print(f"- {len(users)} users created")
    print(f"- {len(alerts)} alerts created")
    print(f"- {len(incidents)} incidents created")
    
    print("\nTest accounts:")
    print("- Admin: admin@exeo.com / password123")
    print("- SOC Analyst: analyst@exeo.com / password123")
    for client in clients:
        client_users = [u for u in users if u.client == client]
        if client_users:
            print(f"- {client.name}: {client_users[0].email} / password123")

if __name__ == '__main__':
    main()
