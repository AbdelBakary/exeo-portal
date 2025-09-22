#!/usr/bin/env python
"""
Script pour corriger le rôle de l'utilisateur roufai@morane.com
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from apps.accounts.models import User, Client

def fix_user_role():
    """Corriger le rôle de l'utilisateur roufai@morane.com"""
    try:
        # Récupérer l'utilisateur
        user = User.objects.get(email='roufai@morane.com')
        print(f"🔍 Utilisateur trouvé: {user.email}")
        print(f"   Rôle actuel: {user.role}")
        print(f"   Client actuel: {user.client}")
        
        # Récupérer le client "aniss"
        client = Client.objects.get(name='aniss')
        print(f"   Client 'aniss' trouvé: {client}")
        
        # Corriger le rôle et le client
        user.role = 'client'
        user.client = client
        user.save()
        
        print(f"✅ Utilisateur corrigé:")
        print(f"   Nouveau rôle: {user.role}")
        print(f"   Nouveau client: {user.client}")
        
        # Vérifier que la correction a fonctionné
        user.refresh_from_db()
        print(f"✅ Vérification: {user.email} - Rôle: {user.role} - Client: {user.client}")
        
    except User.DoesNotExist:
        print("❌ Utilisateur roufai@morane.com non trouvé")
    except Client.DoesNotExist:
        print("❌ Client 'aniss' non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_user_role()
