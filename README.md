# Taxi App - Application de suivi d'activité

Application web Django pour le suivi d'activité des chauffeurs de taxi avec interface Bootstrap responsive.

## 🚀 Fonctionnalités

### Pour les Chauffeurs
- **Connexion sécurisée** avec compte utilisateur
- **Prise de clés** le matin avec signature électronique
- **Remise de clés** le soir avec enregistrement des recettes
- **Signalement de pannes** avec niveaux de sévérité
- **Dashboard personnel** avec historique des activités
- **Suivi des recettes** de la semaine

### Pour les Administrateurs
- **Dashboard global** avec statistiques en temps réel
- **Gestion des chauffeurs** (ajout, modification, désactivation)
- **Suivi des recettes** (journalières, hebdomadaires, mensuelles)
- **Gestion des pannes** avec statuts et priorités
- **Classements et gamification** pour motiver les chauffeurs
- **Interface d'administration Django** complète

## 🛠️ Technologies

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Base de données**: SQLite (extensible à PostgreSQL)
- **Interface**: Responsive design mobile-first

## 📋 Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## 🚀 Installation

1. **Cloner le projet**
   ```bash
   git clone <url-du-repo>
   cd Driver_App
   ```

2. **Installer les dépendances**
   ```bash
   pip install django
   ```

3. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

4. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

5. **Créer des données de test (optionnel)**
   ```bash
   python create_test_data.py
   ```

6. **Démarrer le serveur**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Interface principale: http://localhost:8000
   - Administration Django: http://localhost:8000/admin

## 👥 Comptes de test

Après avoir exécuté `create_test_data.py` :

### Administrateur
- **Utilisateur**: admin
- **Mot de passe**: admin123

### Chauffeurs
- **Jean Dupont**: jean.dupont / chauffeur123
- **Marie Martin**: marie.martin / chauffeur123
- **Pierre Durand**: pierre.durand / chauffeur123

## 📱 Utilisation

### Interface Chauffeur
1. Se connecter avec ses identifiants
2. **Le matin** : Cliquer sur "Prendre les clés"
   - Saisir le niveau de carburant (litres ou %)
   - Signer électroniquement
3. **Le soir** : Cliquer sur "Rendre les clés"
   - Saisir la recette du jour
   - Noter l'état du véhicule
   - Ajouter des observations
   - Signer électroniquement
4. **En cas de problème** : Utiliser "Signaler une panne"

### Interface Administrateur
1. Se connecter en tant qu'admin
2. Accéder au dashboard pour voir les statistiques globales
3. Gérer les chauffeurs via l'interface Django
4. Consulter les recettes et pannes
5. Suivre les classements

## 🏗️ Architecture

```
taxi_app/
├── drivers/           # Application chauffeurs
├── activities/        # Application activités/recettes/pannes
├── admin_dashboard/   # Application dashboard admin
├── templates/         # Templates HTML
├── static/           # Fichiers CSS/JS
└── taxi_app/         # Configuration Django
```

## 📊 Modèles de données

- **Chauffeur**: Informations personnelles et compte utilisateur
- **Activité**: Prise/remise de clés avec détails
- **Recette**: Recettes journalières par chauffeur
- **Panne**: Signalement et suivi des problèmes mécaniques

## 🔧 Configuration

### Base de données
Par défaut SQLite, pour PostgreSQL :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'taxi_app',
        'USER': 'votre_user',
        'PASSWORD': 'votre_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Fuseau horaire
Configuré pour Paris (Europe/Paris) dans `settings.py`

## 🚀 Déploiement

1. Configurer les variables d'environnement
2. Changer `DEBUG = False` en production
3. Configurer la base de données de production
4. Collecter les fichiers statiques : `python manage.py collectstatic`
5. Déployer avec Gunicorn + Nginx

## 🔮 Extensions futures

- API REST avec Django Rest Framework
- Notifications push
- Géolocalisation des véhicules
- Intégration système de paiement
- Rapports PDF automatiques
- Application mobile React Native

## 📝 Licence

Projet développé pour le suivi d'activité de taxi.

## 🤝 Support

Pour toute question ou problème, consulter la documentation Django ou créer une issue.

---

**Développé avec ❤️ en Django + Bootstrap**
