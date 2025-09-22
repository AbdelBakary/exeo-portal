#!/usr/bin/env python
"""
Script to create a superuser for the EXEO Portal.
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/app')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeo_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Client

User = get_user_model()

def create_superuser():
    """Create a superuser and initial client."""
    
    # Create or get the default client
    client, created = Client.objects.get_or_create(
        name='EXEO Security',
        defaults={
            'contact_email': 'admin@exeo.com',
            'contact_phone': '+33 1 23 45 67 89',
            'address': '123 Rue de la Sécurité, 75001 Paris, France',
            'timezone': 'Europe/Paris',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created client: {client.name}")
    else:
        print(f"Using existing client: {client.name}")
    
    # Create superuser
    if not User.objects.filter(email='admin@exeo.com').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@exeo.com',
            password='admin123',
            first_name='Admin',
            last_name='EXEO',
            role='admin',
            client=client,
            is_verified=True
        )
        print(f"Created superuser: {user.email}")
    else:
        print("Superuser already exists")
    
    # Create demo users
    demo_users = [
        {
            'username': 'analyst',
            'email': 'analyst@exeo.com',
            'password': 'analyst123',
            'first_name': 'Jean',
            'last_name': 'Analyste',
            'role': 'soc_analyst',
            'client': client,
        },
        {
            'username': 'client',
            'email': 'client@exeo.com',
            'password': 'client123',
            'first_name': 'Marie',
            'last_name': 'Client',
            'role': 'client',
            'client': client,
        }
    ]
    
    for user_data in demo_users:
        if not User.objects.filter(email=user_data['email']).exists():
            user = User.objects.create_user(**user_data)
            print(f"Created demo user: {user.email}")
        else:
            print(f"Demo user {user_data['email']} already exists")

if __name__ == '__main__':
    create_superuser()
