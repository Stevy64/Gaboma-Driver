#!/usr/bin/env python3
"""
Test simple du formulaire
"""
import requests
import re

def test_simple_form():
    print("=== Test simple du formulaire ===")
    
    # Étape 1: Charger la page de connexion
    print("\n1. Chargement de la page de connexion...")
    response = requests.get('http://localhost:8000/login/')
    print(f"   Status: {response.status_code}")
    
    # Extraire le CSRF token
    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if csrf_token:
        csrf_token = csrf_token.group(1)
        print(f"   CSRF Token: {csrf_token[:20]}...")
    else:
        print("   ❌ CSRF Token non trouvé")
        return
    
    # Étape 2: Soumettre le formulaire
    print("\n2. Soumission du formulaire...")
    response = requests.post('http://localhost:8000/login/', {
        'username': 'chauffeur',
        'password': 'chauffeur123',
        'csrfmiddlewaretoken': csrf_token
    }, cookies=response.cookies, allow_redirects=False)
    
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    
    if response.status_code == 302:
        print("   ✅ Redirection réussie !")
        print(f"   Location: {response.headers.get('Location')}")
    else:
        print("   ❌ Pas de redirection")
        print(f"   Content: {response.text[:500]}...")

if __name__ == '__main__':
    test_simple_form()
