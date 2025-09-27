#!/usr/bin/env python3
"""
Test simple des formulaires
"""

import requests
from bs4 import BeautifulSoup

def test_forms():
    base_url = "http://localhost:8000"
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    try:
        # 1. Se connecter en tant qu'admin
        print("=== Test de connexion admin ===")
        login_url = f"{base_url}/admin/login/"
        response = session.get(login_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
            
            # Connexion admin
            login_data = {
                'username': 'admin',
                'password': 'admin123',
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = session.post(login_url, data=login_data)
            if response.status_code == 302:
                print("✅ Connexion admin réussie")
            else:
                print("❌ Échec de connexion admin")
                return
        else:
            print("❌ Impossible d'accéder à la page de connexion")
            return
        
        # 2. Test du formulaire de création de superviseur
        print("\n=== Test création superviseur ===")
        creer_url = f"{base_url}/admin-dashboard/superviseurs/creer/"
        response = session.get(creer_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
            
            # Données de test
            form_data = {
                'username': 'test_superviseur_2',
                'password': 'test123456',
                'first_name': 'Test',
                'last_name': 'Superviseur 2',
                'email': 'test2@example.com',
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = session.post(creer_url, data=form_data)
            print(f"Status: {response.status_code}")
            print(f"URL de redirection: {response.url}")
            
            if response.status_code == 302:
                print("✅ Formulaire de création soumis avec succès")
            else:
                print("⚠️  Formulaire retourné (erreur possible)")
                # Vérifier les messages d'erreur
                soup = BeautifulSoup(response.text, 'html.parser')
                alerts = soup.find_all('div', class_='alert')
                for alert in alerts:
                    print(f"Message: {alert.get_text().strip()}")
        else:
            print("❌ Impossible d'accéder à la page de création")
        
        # 3. Test du formulaire d'assignation
        print("\n=== Test assignation chauffeurs ===")
        assigner_url = f"{base_url}/admin-dashboard/superviseurs/assigner/1/"
        response = session.get(assigner_url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
            
            # Données de test (assigner les premiers chauffeurs)
            form_data = {
                'chauffeurs': ['1', '2', '3'],
                'csrfmiddlewaretoken': csrf_token
            }
            
            response = session.post(assigner_url, data=form_data)
            print(f"Status: {response.status_code}")
            print(f"URL de redirection: {response.url}")
            
            if response.status_code == 302:
                print("✅ Formulaire d'assignation soumis avec succès")
            else:
                print("⚠️  Formulaire retourné (erreur possible)")
                # Vérifier les messages d'erreur
                soup = BeautifulSoup(response.text, 'html.parser')
                alerts = soup.find_all('div', class_='alert')
                for alert in alerts:
                    print(f"Message: {alert.get_text().strip()}")
        else:
            print("❌ Impossible d'accéder à la page d'assignation")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_forms()

