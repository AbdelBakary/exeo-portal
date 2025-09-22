#!/usr/bin/env python
"""
Script pour vérifier et corriger l'association client-alerte
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import User, Client
from apps.alerts.models import Alert

def check_and_fix_alert():
    """Vérifier et corriger l'alerte roufai12"""
    try:
        # Récupérer l'utilisateur et le client
        user = User.objects.get(email='roufai@morane.com')
        client = user.client
        print(f"🔍 Utilisateur: {user.email}")
        print(f"   Rôle: {user.role}")
        print(f"   Client: {client}")
        
        # Récupérer l'alerte roufai12
        try:
            alert = Alert.objects.get(alert_id='roufai12')
            print(f"🔍 Alerte trouvée: {alert.alert_id}")
            print(f"   Titre: {alert.title}")
            print(f"   Client actuel: {alert.client}")
            
            # Corriger l'association client
            if alert.client != client:
                alert.client = client
                alert.save()
                print(f"✅ Alerte corrigée: client changé vers {client}")
            else:
                print(f"✅ Alerte déjà correcte: client = {client}")
                
        except Alert.DoesNotExist:
            print("❌ Alerte 'roufai12' non trouvée")
            # Lister toutes les alertes
            alerts = Alert.objects.all()[:10]
            print("📋 Premières alertes dans la base:")
            for a in alerts:
                print(f"   - {a.alert_id}: {a.title} (client: {a.client})")
        
        # Vérifier les alertes du client
        client_alerts = Alert.objects.filter(client=client)
        print(f"📊 Alertes du client '{client}': {client_alerts.count()}")
        for alert in client_alerts[:5]:
            print(f"   - {alert.alert_id}: {alert.title}")
            
    except User.DoesNotExist:
        print("❌ Utilisateur roufai@morane.com non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    check_and_fix_alert()
