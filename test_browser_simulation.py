#!/usr/bin/env python3
"""
Simulation de navigateur pour tester la connexion
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

def test_browser_simulation():
    print("=== Simulation de navigateur ===")
    
    client = Client()
    
    # Étape 1: Charger la page de connexion
    print("\n1. Chargement de la page de connexion...")
    response = client.get('/login/')
    print(f"   Status: {response.status_code}")
    
    # Extraire le CSRF token
    content = response.content.decode('utf-8')
    csrf_token = None
    for line in content.split('\n'):
        if 'csrfmiddlewaretoken' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    print(f"   CSRF Token: {csrf_token[:20]}..." if csrf_token else "   ❌ CSRF Token non trouvé")
    
    # Étape 2: Soumettre le formulaire de connexion
    print("\n2. Soumission du formulaire de connexion...")
    if csrf_token:
        response = client.post('/login/', {
            'username': 'chauffeur',
            'password': 'chauffeur123',
            'csrfmiddlewaretoken': csrf_token
        })
    else:
        print("   ❌ Impossible de soumettre sans CSRF token")
        return
    print(f"   Status: {response.status_code}")
    print(f"   Redirection: {response.url if hasattr(response, 'url') else 'Aucune'}")
    
    if response.status_code == 302:
        print("   ✅ Redirection réussie !")
        # Suivre la redirection
        response = client.get(response.url)
        print(f"   Page de destination: {response.status_code}")
        if 'dashboard' in str(response.content):
            print("   ✅ Dashboard chargé !")
        else:
            print("   ❌ Dashboard non trouvé")
    else:
        print("   ❌ Échec de la connexion")
        # Afficher le contenu de la page d'erreur
        content = str(response.content)
        if 'error' in content.lower():
            print("   Message d'erreur détecté dans la réponse")
        if 'success' in content.lower():
            print("   Message de succès détecté dans la réponse")
    
    # Étape 3: Vérifier la session
    print("\n3. Vérification de la session...")
    if client.session.get('_auth_user_id'):
        print(f"   ✅ Utilisateur connecté: {client.session.get('_auth_user_id')}")
    else:
        print("   ❌ Aucun utilisateur connecté")
    
    # Étape 4: Test de création de compte
    print("\n4. Test de création de compte...")
    response = client.get('/creer-compte/')
    print(f"   Status page création: {response.status_code}")
    
    # Extraire le CSRF token pour la création
    content = response.content.decode('utf-8')
    csrf_token = None
    for line in content.split('\n'):
        if 'csrfmiddlewaretoken' in line:
            csrf_token = line.split('value="')[1].split('"')[0]
            break
    
    print(f"   CSRF Token création: {csrf_token[:20]}..." if csrf_token else "   ❌ CSRF Token non trouvé")
    
    response = client.post('/creer-compte/', {
        'nom': 'Test',
        'prenom': 'Nouveau',
        'telephone': '123456789',
        'email': 'nouveau@test.com',
        'username': 'nouveau_test2',
        'password': 'test123',
        'password_confirm': 'test123',
        'csrfmiddlewaretoken': csrf_token
    })
    print(f"   Status création: {response.status_code}")
    print(f"   Redirection: {response.url if hasattr(response, 'url') else 'Aucune'}")

if __name__ == '__main__':
    test_browser_simulation()
