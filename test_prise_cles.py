#!/usr/bin/env python3
"""
Test du formulaire de prise de clés
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

def test_prise_cles():
    print("=== Test du formulaire de prise de clés ===")
    
    client = Client()
    
    # Étape 1: Se connecter
    print("\n1. Connexion...")
    response = client.post('/login/', {
        'username': 'chauffeur',
        'password': 'chauffeur123',
        'csrfmiddlewaretoken': 'test'
    })
    print(f"   Status: {response.status_code}")
    
    # Étape 2: Accéder à la page de prise de clés
    print("\n2. Accès à la page de prise de clés...")
    response = client.get('/prendre-cles/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        # Extraire le CSRF token
        content = response.content.decode('utf-8')
        csrf_token = None
        for line in content.split('\n'):
            if 'csrfmiddlewaretoken' in line:
                csrf_token = line.split('value="')[1].split('"')[0]
                break
        
        print(f"   CSRF Token: {csrf_token[:20]}..." if csrf_token else "   ❌ CSRF Token non trouvé")
        
        # Étape 3: Tester la soumission avec différentes valeurs
        test_values = [
            ("50000", "Test signature", "Valeur normale"),
            ("", "Test signature", "Valeur vide"),
            ("abc", "Test signature", "Valeur non numérique"),
            ("0", "Test signature", "Valeur zéro"),
            ("-100", "Test signature", "Valeur négative"),
            ("  50000  ", "Test signature", "Valeur avec espaces"),
        ]
        
        for value, signature, description in test_values:
            print(f"\n3. Test: {description} ('{value}')")
            response = client.post('/prendre-cles/', {
                'objectif_recette': value,
                'signature': signature,
                'csrfmiddlewaretoken': csrf_token
            })
            print(f"   Status: {response.status_code}")
            if response.status_code == 302:
                print("   ✅ Redirection (succès)")
            else:
                print("   ❌ Pas de redirection")
                # Vérifier les messages d'erreur
                content = str(response.content)
                if 'objectif de recette doit être un nombre entier positif' in content:
                    print("   Message d'erreur: Objectif de recette invalide")
                elif 'obligatoires' in content:
                    print("   Message d'erreur: Champs obligatoires manquants")
    else:
        print("   ❌ Impossible d'accéder à la page")

if __name__ == '__main__':
    test_prise_cles()
