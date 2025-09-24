#!/usr/bin/env python3
"""
Test des messages dans les templates
"""
import requests
import re

def test_messages():
    print("=== Test des messages ===")
    
    # Test 1: Connexion avec mauvais mot de passe
    print("\n1. Test avec mauvais mot de passe...")
    response = requests.get('http://localhost:8000/login/')
    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if csrf_token:
        csrf_token = csrf_token.group(1)
        
        response = requests.post('http://localhost:8000/login/', {
            'username': 'chauffeur',
            'password': 'mauvais_mot_de_passe',
            'csrfmiddlewaretoken': csrf_token
        }, cookies=response.cookies, allow_redirects=True)
        
        print(f"   Status: {response.status_code}")
        if 'error' in response.text.lower() or 'incorrect' in response.text.lower():
            print("   ✅ Message d'erreur détecté")
        else:
            print("   ❌ Aucun message d'erreur détecté")
    
    # Test 2: Connexion avec bon mot de passe
    print("\n2. Test avec bon mot de passe...")
    response = requests.get('http://localhost:8000/login/')
    csrf_token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
    if csrf_token:
        csrf_token = csrf_token.group(1)
        
        response = requests.post('http://localhost:8000/login/', {
            'username': 'chauffeur',
            'password': 'chauffeur123',
            'csrfmiddlewaretoken': csrf_token
        }, cookies=response.cookies, allow_redirects=True)
        
        print(f"   Status: {response.status_code}")
        if 'dashboard' in response.text.lower():
            print("   ✅ Dashboard chargé")
        if 'bienvenue' in response.text.lower():
            print("   ✅ Message de bienvenue détecté")
        else:
            print("   ❌ Aucun message de bienvenue détecté")

if __name__ == '__main__':
    test_messages()
