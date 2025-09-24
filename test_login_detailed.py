#!/usr/bin/env python3
"""
Script de test détaillé pour la connexion
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

def test_detailed_login():
    print("=== Test détaillé de connexion ===")
    
    client = Client()
    
    # Test 1: Vérifier les chauffeurs existants
    print("\n1. Chauffeurs dans la base de données:")
    chauffeurs = Chauffeur.objects.all()
    for chauffeur in chauffeurs:
        print(f"   - {chauffeur.nom} {chauffeur.prenom}")
        print(f"     User: {chauffeur.user.username if chauffeur.user else 'Aucun'}")
        print(f"     Actif: {chauffeur.actif}")
        print(f"     Email: {chauffeur.email}")
        print()
    
    # Test 2: Test de connexion avec chauffeur/chauffeur123
    print("2. Test de connexion avec chauffeur/chauffeur123...")
    response = client.post('/login/', {
        'username': 'chauffeur',
        'password': 'chauffeur123'
    })
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
    
    # Test 3: Vérifier la session
    print("\n3. Vérification de la session...")
    if client.session.get('_auth_user_id'):
        print(f"   ✅ Utilisateur connecté: {client.session.get('_auth_user_id')}")
    else:
        print("   ❌ Aucun utilisateur connecté")
    
    # Test 4: Test de création de compte
    print("\n4. Test de création de compte...")
    response = client.post('/creer-compte/', {
        'nom': 'Test',
        'prenom': 'Nouveau',
        'telephone': '123456789',
        'email': 'nouveau@test.com',
        'username': 'nouveau_test',
        'password': 'test123',
        'password_confirm': 'test123'
    })
    print(f"   Status: {response.status_code}")
    print(f"   Redirection: {response.url if hasattr(response, 'url') else 'Aucune'}")
    
    if response.status_code == 302:
        print("   ✅ Redirection réussie !")
        # Suivre la redirection
        response = client.get(response.url)
        print(f"   Page de destination: {response.status_code}")
    else:
        print("   ❌ Échec de la création de compte")
        content = str(response.content)
        if 'error' in content.lower():
            print("   Message d'erreur détecté dans la réponse")
        if 'success' in content.lower():
            print("   Message de succès détecté dans la réponse")

if __name__ == '__main__':
    test_detailed_login()
