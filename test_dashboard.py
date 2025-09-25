#!/usr/bin/env python3
"""
Test du dashboard chauffeur avec les nouvelles données
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxi_app.settings')
django.setup()

# Ajouter testserver aux ALLOWED_HOSTS pour les tests
from django.conf import settings
settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.contrib.auth.models import User
from drivers.models import Chauffeur
from activities.models import PriseCles, RemiseCles, Panne
from datetime import date, time
from django.utils import timezone

def test_dashboard():
    print("=== Test du dashboard chauffeur ===")
    
    client = Client()
    
    # Se connecter
    print("\n1. Connexion...")
    response = client.post('/login/', {
        'username': 'chauffeur',
        'password': 'chauffeur123',
        'csrfmiddlewaretoken': 'test'
    })
    print(f"   Status: {response.status_code}")
    
    # Accéder au dashboard
    print("\n2. Accès au dashboard...")
    response = client.get('/dashboard/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Vérifier les sections
        if 'Activités récentes' in content:
            print("   ✅ Section 'Activités récentes' trouvée")
        else:
            print("   ❌ Section 'Activités récentes' manquante")
            
        if 'Recettes de la semaine' in content:
            print("   ✅ Section 'Recettes de la semaine' trouvée")
        else:
            print("   ❌ Section 'Recettes de la semaine' manquante")
            
        if 'Pannes récentes' in content:
            print("   ✅ Section 'Pannes récentes' trouvée")
        else:
            print("   ❌ Section 'Pannes récentes' manquante")
            
        # Vérifier les statistiques
        if 'Total' in content and 'Moyenne' in content:
            print("   ✅ Statistiques de la semaine trouvées")
        else:
            print("   ❌ Statistiques de la semaine manquantes")
            
        # Vérifier les icônes
        if 'bi-key-fill' in content and 'bi-key' in content:
            print("   ✅ Icônes des activités trouvées")
        else:
            print("   ❌ Icônes des activités manquantes")
            
        if 'bi-fuel-pump' in content:
            print("   ✅ Icônes de carburant trouvées")
        else:
            print("   ❌ Icônes de carburant manquantes")
    else:
        print("   ❌ Impossible d'accéder au dashboard")

if __name__ == '__main__':
    test_dashboard()
