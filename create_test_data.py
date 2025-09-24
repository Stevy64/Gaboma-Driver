#!/usr/bin/env python
"""
Script pour créer des données de test pour l'application Taxi
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxi_app.settings')
django.setup()

from django.contrib.auth.models import User
from drivers.models import Chauffeur
from activities.models import Activite, Recette, Panne
from datetime import datetime, date, timedelta
from django.utils import timezone
import random

def create_test_data():
    print("Création des données de test...")
    
    # Créer des utilisateurs chauffeurs
    chauffeurs_data = [
        {'username': 'jean.dupont', 'first_name': 'Jean', 'last_name': 'Dupont', 'email': 'jean.dupont@taxi.com'},
        {'username': 'marie.martin', 'first_name': 'Marie', 'last_name': 'Martin', 'email': 'marie.martin@taxi.com'},
        {'username': 'pierre.durand', 'first_name': 'Pierre', 'last_name': 'Durand', 'email': 'pierre.durand@taxi.com'},
    ]
    
    chauffeurs = []
    for data in chauffeurs_data:
        user, created = User.objects.get_or_create(
            username=data['username'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'email': data['email'],
            }
        )
        if created:
            user.set_password('chauffeur123')
            user.save()
        
        chauffeur, created = Chauffeur.objects.get_or_create(
            user=user,
            defaults={
                'nom': data['last_name'],
                'prenom': data['first_name'],
                'telephone': f'0{random.randint(100000000, 999999999)}',
                'email': data['email'],
                'actif': True
            }
        )
        chauffeurs.append(chauffeur)
        print(f"Chauffeur créé : {chauffeur.nom_complet}")
    
    # Créer des activités et recettes pour les 7 derniers jours
    today = date.today()
    for i in range(7):
        current_date = today - timedelta(days=i)
        
        for chauffeur in chauffeurs:
            # Activité de prise de clés (matin)
            prise_heure = timezone.make_aware(datetime.combine(current_date, datetime.min.time().replace(hour=8, minute=random.randint(0, 30))))
            Activite.objects.get_or_create(
                chauffeur=chauffeur,
                type_activite='prise',
                date_heure=prise_heure,
                defaults={
                    'carburant_pourcentage': random.randint(20, 90),
                    'signature': f'Signature de {chauffeur.prenom} {chauffeur.nom}'
                }
            )
            
            # Activité de remise de clés (soir)
            remise_heure = timezone.make_aware(datetime.combine(current_date, datetime.min.time().replace(hour=18, minute=random.randint(0, 30))))
            recette_jour = round(random.uniform(80, 200), 2)
            
            Activite.objects.get_or_create(
                chauffeur=chauffeur,
                type_activite='remise',
                date_heure=remise_heure,
                defaults={
                    'recette_jour': recette_jour,
                    'etat_vehicule': random.choice(['excellent', 'bon', 'moyen']),
                    'notes': f'Journée normale du {current_date.strftime("%d/%m/%Y")}',
                    'signature': f'Signature de {chauffeur.prenom} {chauffeur.nom}'
                }
            )
            
            # Recette du jour
            Recette.objects.get_or_create(
                chauffeur=chauffeur,
                date=current_date,
                defaults={'montant': recette_jour}
            )
    
    # Créer quelques pannes
    pannes_data = [
        {'chauffeur': chauffeurs[0], 'severite': 'mineure', 'description': 'Bruit anormal au niveau de la porte avant droite'},
        {'chauffeur': chauffeurs[1], 'severite': 'moderee', 'description': 'Problème de climatisation, air chaud seulement'},
        {'chauffeur': chauffeurs[2], 'severite': 'majeure', 'description': 'Freins qui grincent, inspection nécessaire'},
    ]
    
    for panne_data in pannes_data:
        Panne.objects.get_or_create(
            chauffeur=panne_data['chauffeur'],
            description=panne_data['description'],
            defaults={
                'severite': panne_data['severite'],
                'statut': 'signalee'
            }
        )
        print(f"Panne créée : {panne_data['description']}")
    
    print(f"\nDonnées de test créées avec succès !")
    print(f"- {len(chauffeurs)} chauffeurs")
    print(f"- Activités et recettes pour 7 jours")
    print(f"- {len(pannes_data)} pannes")
    print(f"\nIdentifiants de test :")
    print(f"- Admin : admin / admin123")
    for chauffeur in chauffeurs:
        print(f"- Chauffeur {chauffeur.nom_complet} : {chauffeur.user.username} / chauffeur123")

if __name__ == '__main__':
    create_test_data()
