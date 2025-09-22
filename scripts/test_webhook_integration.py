#!/usr/bin/env python3
"""
Script de test pour l'intégration webhook
Teste la collecte automatique des alertes via webhook
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timezone

# Configuration Django
sys.path.append('/Users/imanebakary/exeo-portal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import Client, User
from apps.integrations.models import ClientIntegration, AlertMappingTemplate
from apps.alerts.models import Alert


def create_test_client():
    """Crée un client de test"""
    client, created = Client.objects.get_or_create(
        name="Test Client",
        defaults={
            'contact_email': 'test@client.com',
            'contact_phone': '+33123456789',
            'address': '123 Test Street, Paris, France'
        }
    )
    print(f"✅ Client {'créé' if created else 'trouvé'}: {client.name}")
    return client


def create_test_integration(client):
    """Crée une intégration de test"""
    # Générer un token API unique
    import uuid
    api_token = str(uuid.uuid4())
    
    integration, created = ClientIntegration.objects.get_or_create(
        client=client,
        name="Test Webhook Integration",
        defaults={
            'integration_type': 'webhook',
            'endpoint_url': 'https://test-client.com/webhook',
            'api_token': api_token,
            'mapping_config': {
                'id': {'path': 'external_id', 'type': 'string'},
                'title': {'path': 'title', 'type': 'string'},
                'description': {'path': 'description', 'type': 'string'},
                'severity': {'path': 'severity', 'type': 'string'},
                'alert_type': {'path': 'alert_type', 'type': 'string'},
                'source_ip': {'path': 'source_ip', 'type': 'ip'},
                'destination_ip': {'path': 'destination_ip', 'type': 'ip'},
                'timestamp': {'path': 'timestamp', 'format': 'iso8601'}
            },
            'is_active': True,
            'status': 'active'
        }
    )
    
    if created:
        print(f"✅ Intégration créée: {integration.name}")
        print(f"   Token API: {api_token}")
    else:
        print(f"✅ Intégration trouvée: {integration.name}")
        api_token = integration.api_token
    
    return integration, api_token


def create_mapping_templates():
    """Crée des templates de mapping par défaut"""
    templates_data = [
        {
            'name': 'Splunk Default',
            'system_type': 'splunk',
            'mapping_config': {
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
            'description': 'Configuration par défaut pour Splunk'
        },
        {
            'name': 'Fortinet Default',
            'system_type': 'fortinet',
            'mapping_config': {
                'id': {'path': 'logid', 'type': 'string'},
                'title': {'path': 'action', 'type': 'string'},
                'description': {'path': 'msg', 'type': 'string'},
                'severity': {
                    'path': 'level',
                    'mapping': {
                        'emergency': 'critical', 'alert': 'high', 'critical': 'high',
                        'error': 'medium', 'warning': 'medium', 'notice': 'low', 'info': 'low'
                    }
                },
                'source_ip': {'path': 'srcip', 'type': 'ip'},
                'destination_ip': {'path': 'dstip', 'type': 'ip'},
                'timestamp': {'path': 'time', 'format': 'iso8601'}
            },
            'description': 'Configuration par défaut pour Fortinet'
        }
    ]
    
    for template_data in templates_data:
        template, created = AlertMappingTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        print(f"✅ Template {'créé' if created else 'trouvé'}: {template.name}")


def test_webhook_api(api_token):
    """Teste l'API webhook avec des données simulées"""
    base_url = "http://localhost:8000"
    webhook_url = f"{base_url}/api/integrations/webhook/"
    
    # Données de test
    import time
    timestamp = int(time.time())
    
    test_alerts = [
        {
            "external_id": f"TEST-ALERT-{timestamp}-001",
            "title": "Suspicious Login Attempts",
            "description": "Multiple failed login attempts detected from suspicious IP",
            "severity": "high",
            "alert_type": "intrusion",
            "source_ip": "192.168.1.100",
            "destination_ip": "10.0.0.1",
            "source_port": 12345,
            "destination_port": 22,
            "protocol": "TCP",
            "source_system": "Test SIEM",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_data": {
                "event_id": "TEST-ALERT-001",
                "user": "admin",
                "attempts": 5,
                "blocked": True
            },
            "tags": ["authentication", "intrusion", "blocked"]
        },
        {
            "external_id": f"TEST-ALERT-{timestamp}-002",
            "title": "Malware Detection",
            "description": "Malicious file detected on endpoint",
            "severity": "critical",
            "alert_type": "malware",
            "source_ip": "10.0.0.50",
            "destination_ip": "10.0.0.1",
            "source_port": None,
            "destination_port": None,
            "protocol": "",
            "source_system": "Test EDR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_data": {
                "event_id": "TEST-ALERT-002",
                "file_hash": "abc123def456",
                "file_name": "suspicious.exe",
                "quarantined": True
            },
            "tags": ["malware", "quarantined", "endpoint"]
        },
        {
            "external_id": f"TEST-ALERT-{timestamp}-003",
            "title": "DDoS Attack Detected",
            "description": "High volume of traffic detected from multiple sources",
            "severity": "critical",
            "alert_type": "ddos",
            "source_ip": "203.0.113.1",
            "destination_ip": "10.0.0.100",
            "source_port": None,
            "destination_port": 80,
            "protocol": "TCP",
            "source_system": "Test Firewall",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_data": {
                "event_id": "TEST-ALERT-003",
                "packets_per_second": 10000,
                "sources_count": 1000,
                "mitigation_active": True
            },
            "tags": ["ddos", "mitigation", "network"]
        }
    ]
    
    headers = {
        'X-Client-Token': api_token,
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧪 Test de l'API webhook: {webhook_url}")
    
    for i, alert_data in enumerate(test_alerts, 1):
        print(f"\n📤 Envoi de l'alerte {i}: {alert_data['title']}")
        
        try:
            response = requests.post(
                webhook_url,
                headers=headers,
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Succès: {result['message']}")
                print(f"   Alert ID: {result['alert_id']}")
                print(f"   Risk Score: {result['risk_score']}")
            else:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {str(e)}")
    
    # Test du statut du webhook
    print(f"\n🔍 Test du statut du webhook...")
    try:
        status_response = requests.get(f"{base_url}/api/integrations/webhook/status/", timeout=5)
        if status_response.status_code == 200:
            print(f"✅ Webhook opérationnel: {status_response.json()['message']}")
        else:
            print(f"❌ Webhook non disponible: {status_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de contacter le webhook: {str(e)}")


def test_webhook_validation(api_token):
    """Teste la validation du webhook"""
    base_url = "http://localhost:8000"
    test_url = f"{base_url}/api/integrations/webhook/test/"
    
    headers = {
        'X-Client-Token': api_token,
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔍 Test de validation du webhook...")
    
    try:
        response = requests.post(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Validation réussie: {result['message']}")
            print(f"   Intégration: {result['integration']['name']}")
            print(f"   Type: {result['integration']['type']}")
            print(f"   Client: {result['integration']['client']}")
        else:
            print(f"❌ Validation échouée: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de validation: {str(e)}")


def check_created_alerts():
    """Vérifie les alertes créées"""
    print(f"\n📊 Vérification des alertes créées...")
    
    total_alerts = Alert.objects.count()
    recent_alerts = Alert.objects.filter(
        created_at__gte=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    print(f"   Total d'alertes: {total_alerts}")
    print(f"   Alertes d'aujourd'hui: {recent_alerts}")
    
    # Afficher les dernières alertes
    latest_alerts = Alert.objects.order_by('-created_at')[:5]
    print(f"\n📋 Dernières alertes:")
    for alert in latest_alerts:
        print(f"   - {alert.alert_id}: {alert.title} (Score: {alert.risk_score:.2f})")


def main():
    """Fonction principale de test"""
    print("🚀 DÉMARRAGE DES TESTS D'INTÉGRATION WEBHOOK")
    print("=" * 50)
    
    try:
        # 1. Créer le client de test
        client = create_test_client()
        
        # 2. Créer l'intégration de test
        integration, api_token = create_test_integration(client)
        
        # 3. Créer les templates de mapping
        create_mapping_templates()
        
        # 4. Tester l'API webhook
        test_webhook_api(api_token)
        
        # 5. Tester la validation
        test_webhook_validation(api_token)
        
        # 6. Vérifier les alertes créées
        check_created_alerts()
        
        print(f"\n✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS!")
        print(f"🔑 Token API pour les tests: {api_token}")
        print(f"🌐 URL du webhook: http://localhost:8000/api/integrations/webhook/")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
