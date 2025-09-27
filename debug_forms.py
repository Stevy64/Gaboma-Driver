#!/usr/bin/env python3
"""
Script de debug pour diagnostiquer les problèmes de soumission des formulaires.
"""

import requests
import sys
import re

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_csrf_token(session, url):
    """Récupère le token CSRF d'une page"""
    response = session.get(url)
    if response.status_code != 200:
        return None
    
    csrf_match = re.search(r'name="csrfmiddlewaretoken".*?value="([^"]+)"', response.text)
    if csrf_match:
        return csrf_match.group(1)
    return None

def debug_form_submission():
    """Debug la soumission des formulaires"""
    
    # Créer une session pour maintenir les cookies
    session = requests.Session()
    
    print("🔐 Connexion à l'admin Django...")
    
    # 1. Se connecter à l'admin Django
    login_url = f"{BASE_URL}/admin/login/"
    csrf_token = get_csrf_token(session, login_url)
    
    if not csrf_token:
        print("❌ Erreur: Token CSRF non trouvé")
        return False
    
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD,
        'next': '/admin/',
        'csrfmiddlewaretoken': csrf_token
    }
    
    # Se connecter
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if response.status_code != 200 or 'admin' not in response.url:
        print(f"❌ Erreur: Échec de la connexion admin ({response.status_code})")
        return False
    
    print("✅ Connexion admin réussie")
    
    # 2. Tester la création de superviseur
    print("\n➕ Test de création de superviseur...")
    creer_url = f"{BASE_URL}/admin-dashboard/superviseurs/creer/"
    
    # GET pour récupérer le formulaire
    response = session.get(creer_url)
    if response.status_code != 200:
        print(f"❌ Erreur: Page de création inaccessible ({response.status_code})")
        return False
    
    print("✅ Page de création accessible")
    
    # Vérifier l'action du formulaire
    if 'action="' in response.text and 'creer_superviseur' in response.text:
        print("✅ Action du formulaire correcte")
    else:
        print("❌ Action du formulaire manquante ou incorrecte")
        print("Contenu du formulaire:")
        for line in response.text.split('\n'):
            if 'form' in line.lower():
                print(f"  {line.strip()}")
    
    # Récupérer le token CSRF
    csrf_token = get_csrf_token(session, creer_url)
    if not csrf_token:
        print("❌ Erreur: Token CSRF non trouvé sur la page de création")
        return False
    
    # Données de test
    form_data = {
        'username': 'test_debug_123',
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'Debug',
        'password': 'testpassword123',
        'csrfmiddlewaretoken': csrf_token
    }
    
    print(f"📝 Soumission du formulaire avec token CSRF: {csrf_token[:10]}...")
    
    # POST pour soumettre le formulaire
    response = session.post(creer_url, data=form_data, allow_redirects=True)
    
    print(f"📊 Réponse POST:")
    print(f"  - Status Code: {response.status_code}")
    print(f"  - URL finale: {response.url}")
    print(f"  - Taille de la réponse: {len(response.text)} caractères")
    
    if response.status_code == 200:
        if "créé avec succès" in response.text:
            print("✅ Superviseur créé avec succès")
        elif "existe déjà" in response.text:
            print("⚠️  Superviseur existe déjà (normal si testé plusieurs fois)")
        elif "error" in response.text.lower():
            print("❌ Erreur détectée dans la réponse")
            # Chercher les messages d'erreur
            for line in response.text.split('\n'):
                if 'error' in line.lower() or 'alert' in line.lower():
                    print(f"  Erreur: {line.strip()}")
        else:
            print("⚠️  Réponse inattendue - vérifier le contenu")
    elif response.status_code == 302:
        print("✅ Redirection après soumission (normal)")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
    
    # 3. Tester l'assignation de chauffeurs
    print("\n🔗 Test d'assignation de chauffeurs...")
    
    # Trouver un superviseur existant
    superviseurs_url = f"{BASE_URL}/admin-dashboard/superviseurs/"
    response = session.get(superviseurs_url)
    
    if response.status_code != 200:
        print(f"❌ Erreur: Page superviseurs inaccessible ({response.status_code})")
        return False
    
    # Chercher un lien d'assignation
    assignation_links = re.findall(r'href="([^"]*assigner/\d+/)"', response.text)
    if not assignation_links:
        print("❌ Erreur: Aucun lien d'assignation trouvé")
        return False
    
    superviseur_id = assignation_links[0].split('/assigner/')[1].split('/')[0]
    print(f"✅ Superviseur trouvé (ID: {superviseur_id})")
    
    assignation_url = f"{BASE_URL}/admin-dashboard/superviseurs/assigner/{superviseur_id}/"
    response = session.get(assignation_url)
    
    if response.status_code != 200:
        print(f"❌ Erreur: Page d'assignation inaccessible ({response.status_code})")
        return False
    
    print("✅ Page d'assignation accessible")
    
    # Vérifier l'action du formulaire
    if 'action="' in response.text and 'assigner_chauffeurs' in response.text:
        print("✅ Action du formulaire correcte")
    else:
        print("❌ Action du formulaire manquante ou incorrecte")
    
    # Récupérer le token CSRF
    csrf_token = get_csrf_token(session, assignation_url)
    if not csrf_token:
        print("❌ Erreur: Token CSRF non trouvé sur la page d'assignation")
        return False
    
    # Extraire les IDs des chauffeurs
    chauffeur_ids = re.findall(r'name="chauffeurs".*?value="(\d+)"', response.text)
    if not chauffeur_ids:
        print("❌ Erreur: Aucun chauffeur trouvé pour l'assignation")
        return False
    
    print(f"✅ {len(chauffeur_ids)} chauffeurs trouvés")
    
    # Données de test pour l'assignation
    form_data = {
        'chauffeurs': [chauffeur_ids[0]],  # Sélectionner le premier chauffeur
        'csrfmiddlewaretoken': csrf_token
    }
    
    print(f"📝 Soumission du formulaire d'assignation avec token CSRF: {csrf_token[:10]}...")
    
    # POST pour soumettre le formulaire
    response = session.post(assignation_url, data=form_data, allow_redirects=True)
    
    print(f"📊 Réponse POST:")
    print(f"  - Status Code: {response.status_code}")
    print(f"  - URL finale: {response.url}")
    print(f"  - Taille de la réponse: {len(response.text)} caractères")
    
    if response.status_code == 200:
        if "assignations mises à jour" in response.text.lower():
            print("✅ Assignations mises à jour avec succès")
        elif "error" in response.text.lower():
            print("❌ Erreur détectée dans la réponse")
            # Chercher les messages d'erreur
            for line in response.text.split('\n'):
                if 'error' in line.lower() or 'alert' in line.lower():
                    print(f"  Erreur: {line.strip()}")
        else:
            print("⚠️  Réponse inattendue - vérifier le contenu")
    elif response.status_code == 302:
        print("✅ Redirection après soumission (normal)")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
    
    print("\n🎉 Debug terminé!")
    return True

if __name__ == "__main__":
    print("🔍 Debug des formulaires de gestion des superviseurs")
    print("=" * 60)
    
    try:
        debug_form_submission()
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
