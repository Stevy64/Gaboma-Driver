# 🚕 Gaboma Drive - Application de Suivi d'Activité

Application Django complète pour la gestion des chauffeurs de taxi avec système de prise/remise de clés et suivi des performances.

## ✨ Fonctionnalités

### 👨‍💼 Gestion des Chauffeurs
- Inscription et authentification des chauffeurs
- Profils complets avec informations de contact
- Système de statut actif/inactif

### 🔑 Système de Prise/Remise de Clés
- **Prise de clés (matin)** : Définition d'objectifs de recette
- **Remise de clés (soir)** : Saisie des recettes réalisées
- **Signature électronique** : Validation obligatoire des actions
- **Contraintes métier** : Une seule prise/remise par jour par chauffeur

### 📊 Dashboard et Statistiques
- **Dashboard chauffeur** : Actions contextuelles selon l'état
- **Dashboard admin** : Vue d'ensemble de l'activité
- **Statistiques** : Suivi des performances et recettes
- **Historique** : Activités récentes et tendances

### 🎮 Système de Gamification
- **Messages motivants** : Feedback selon la performance
- **Calcul automatique** : Comparaison objectif vs réalisé
- **Indicateurs visuels** : Alertes colorées selon les résultats
- **Classements** : Top des chauffeurs par performance

### 🛠️ Gestion des Pannes
- Signalement des problèmes mécaniques
- Niveaux de sévérité (mineure, modérée, critique)
- Suivi des résolutions
- Historique des interventions

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip
- Git

### Installation
```bash
# Cloner le dépôt
git clone https://github.com/votre-username/gaboma-drive.git
cd gaboma-drive

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur
python manage.py runserver
```

## 🎯 Utilisation

### Connexion Chauffeur
1. Allez à `http://localhost:8000/login/`
2. Utilisez les identifiants fournis par l'administrateur
3. Accédez au dashboard chauffeur

### Connexion Admin
1. Allez à `http://localhost:8000/admin/`
2. Utilisez les identifiants du superutilisateur
3. Gérez les chauffeurs et consultez les statistiques

### Workflow Chauffeur
1. **Matin** : Prendre les clés avec objectif de recette
2. **Journée** : Effectuer les courses
3. **Soir** : Remettre les clés avec recette réalisée
4. **Feedback** : Recevoir le message de performance

## 🏗️ Architecture

### Modèles Django
- **Chauffeur** : Informations des chauffeurs
- **PriseCles** : Prise de clés du matin
- **RemiseCles** : Remise de clés du soir
- **Activite** : Activités générales (legacy)
- **Recette** : Recettes journalières
- **Panne** : Signalements de pannes

### Applications
- **drivers** : Gestion des chauffeurs et authentification
- **activities** : Suivi des activités et pannes
- **admin_dashboard** : Interface d'administration

### Technologies
- **Backend** : Django 4.2.7
- **Frontend** : Bootstrap 5, HTML5, CSS3, JavaScript
- **Base de données** : SQLite (développement), PostgreSQL (production)
- **Authentification** : Django Auth System

## 📱 Interface

### Design Responsive
- **Mobile-first** : Optimisé pour smartphones
- **Bootstrap 5** : Framework CSS moderne
- **Icônes** : Bootstrap Icons pour la navigation
- **Couleurs** : Palette cohérente et professionnelle

### Expérience Utilisateur
- **Navigation intuitive** : Actions contextuelles
- **Validation en temps réel** : Feedback immédiat
- **Messages clairs** : Instructions et erreurs explicites
- **Accessibilité** : Labels et descriptions complètes

## 🔧 Configuration

### Variables d'Environnement
```python
# settings.py
SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Base de Données
```python
# SQLite (développement)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# PostgreSQL (production)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gaboma_drive',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🧪 Tests

### Tests Unitaires
```bash
python manage.py test
```

### Tests de Fonctionnalités
- Authentification des chauffeurs
- Prise/remise de clés
- Calcul des performances
- Gestion des pannes

## 📈 Performance

### Optimisations
- **Requêtes optimisées** : select_related et prefetch_related
- **Cache** : Mise en cache des statistiques
- **Pagination** : Limitation des résultats
- **Indexation** : Index sur les champs fréquemment utilisés

### Monitoring
- **Logs** : Suivi des erreurs et activités
- **Métriques** : Temps de réponse et utilisation
- **Alertes** : Notifications en cas de problème

## 🚀 Déploiement

### Production
1. **Serveur web** : Nginx + Gunicorn
2. **Base de données** : PostgreSQL
3. **Fichiers statiques** : CDN ou serveur dédié
4. **SSL** : Certificat HTTPS
5. **Monitoring** : Logs et métriques

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "gaboma_drive.wsgi:application"]
```

## 🤝 Contribution

### Développement
1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

### Standards
- **PEP 8** : Style de code Python
- **Tests** : Couverture de code > 80%
- **Documentation** : Docstrings et README
- **Commits** : Messages clairs et descriptifs

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour toute question ou problème :
- **Issues** : Utilisez le système d'issues GitHub
- **Email** : support@taxi-app.com
- **Documentation** : Consultez la documentation complète

---

**🚕 Développé avec ❤️ pour améliorer la gestion des flottes de taxi**
