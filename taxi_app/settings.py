# =============================================================================
# CONFIGURATION DJANGO - Gaboma Drive Application
# =============================================================================
"""
Configuration Django pour l'application Gaboma Drive

Ce fichier contient tous les paramètres de configuration pour l'application
de suivi d'activité de taxi. Il définit les applications installées, la base
de données, les templates, les fichiers statiques, et les paramètres de sécurité.

Application : Gaboma Drive
Version : 1.0
Django : 4.2.7
Base de données : SQLite (développement) / PostgreSQL (production)
"""

from pathlib import Path

# =============================================================================
# CONFIGURATION DES CHEMINS - Définition des répertoires du projet
# =============================================================================

# Chemin de base du projet Django
# Utilise pathlib.Path pour une gestion moderne des chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# CONFIGURATION DE SÉCURITÉ - Paramètres critiques pour la production
# =============================================================================

# Clé secrète Django - CRITIQUE : À changer en production !
# Cette clé est utilisée pour le chiffrement des sessions et autres données sensibles
SECRET_KEY = 'django-insecure-xp$xfl!*hgtwk^faifx$3(0e&fn5ci48t(1l#z*n9gbk66jc$$'

# Mode debug - DÉSACTIVER en production !
# DEBUG = True affiche des erreurs détaillées (utile en développement)
DEBUG = True

# Hôtes autorisés - Liste des domaines/IP autorisés à servir l'application
# En production, remplacer par les vrais domaines
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', 'testserver']

# =============================================================================
# CONFIGURATION DES APPLICATIONS - Modules Django installés
# =============================================================================

INSTALLED_APPS = [
    # Applications Django par défaut
    'django.contrib.admin',        # Interface d'administration
    'django.contrib.auth',         # Système d'authentification
    'django.contrib.contenttypes', # Framework de types de contenu
    'django.contrib.sessions',     # Gestion des sessions
    'django.contrib.messages',     # Système de messages
    'django.contrib.staticfiles',  # Gestion des fichiers statiques
    
    # Applications personnalisées de Gaboma Drive
    'drivers',          # Gestion des chauffeurs
    'activities',       # Gestion des activités (prises/remises de clés)
    'admin_dashboard',  # Tableau de bord administrateur
]

# =============================================================================
# CONFIGURATION DES MIDDLEWARES - Composants de traitement des requêtes
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Sécurité générale
    'django.contrib.sessions.middleware.SessionMiddleware',    # Gestion des sessions
    'django.middleware.common.CommonMiddleware',               # Middleware commun
    'django.middleware.csrf.CsrfViewMiddleware',               # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentification
    'django.contrib.messages.middleware.MessageMiddleware',    # Messages utilisateur
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Protection clickjacking
]

# =============================================================================
# CONFIGURATION DES URLS - Point d'entrée du routage
# =============================================================================

ROOT_URLCONF = 'taxi_app.urls'

# =============================================================================
# CONFIGURATION DES TEMPLATES - Moteur de rendu des vues
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Répertoire global des templates
        'APP_DIRS': True,                  # Recherche dans les dossiers templates des apps
        'OPTIONS': {
            'context_processors': [
                # Processeurs de contexte disponibles dans tous les templates
                'django.template.context_processors.debug',      # Variables de debug
                'django.template.context_processors.request',    # Objet request
                'django.contrib.auth.context_processors.auth',   # Utilisateur connecté
                'django.contrib.messages.context_processors.messages',  # Messages
            ],
        },
    },
]

# =============================================================================
# CONFIGURATION WSGI - Interface de déploiement
# =============================================================================

WSGI_APPLICATION = 'taxi_app.wsgi.application'

# =============================================================================
# CONFIGURATION DE LA BASE DE DONNÉES - Stockage des données
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',    # Moteur SQLite pour le développement
        'NAME': BASE_DIR / 'db.sqlite3',           # Fichier de base SQLite
    }
}

# Configuration alternative pour PostgreSQL en production :
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'gaboma_drive',
#         'USER': 'your_username',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# =============================================================================
# VALIDATION DES MOTS DE PASSE - Sécurité des comptes utilisateurs
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Empêche l'utilisation d'informations personnelles dans le mot de passe
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Longueur minimale du mot de passe
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Empêche l'utilisation de mots de passe courants
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Empêche les mots de passe entièrement numériques
    },
]

# =============================================================================
# CONFIGURATION INTERNATIONALE - Langue et fuseau horaire
# =============================================================================

LANGUAGE_CODE = 'fr-fr'        # Langue française
TIME_ZONE = 'Europe/Paris'     # Fuseau horaire de Paris (Gabon)
USE_I18N = True                # Activation de l'internationalisation
USE_TZ = True                  # Utilisation des fuseaux horaires

# =============================================================================
# CONFIGURATION DES FICHIERS STATIQUES - CSS, JavaScript, Images
# =============================================================================

STATIC_URL = 'static/'                    # URL de base pour les fichiers statiques
STATICFILES_DIRS = [
    BASE_DIR / "static",                  # Répertoire des fichiers statiques de développement
]
STATIC_ROOT = BASE_DIR / "staticfiles"    # Répertoire de collecte pour la production

# =============================================================================
# CONFIGURATION DES CLÉS PRIMAIRES - Type de clé par défaut
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# CONFIGURATION DE L'AUTHENTIFICATION - Redirections après connexion/déconnexion
# =============================================================================

# Redirection après une connexion réussie
LOGIN_REDIRECT_URL = 'drivers:dashboard_chauffeur'

# URL de connexion pour les utilisateurs non authentifiés
LOGIN_URL = 'drivers:login_chauffeur'

# Redirection après déconnexion
LOGOUT_REDIRECT_URL = 'drivers:index'

# =============================================================================
# PAGES D'ERREUR PERSONNALISÉES - Gestion esthétique des erreurs
# =============================================================================

# Configuration des pages d'erreur personnalisées
# Ces templates seront utilisés automatiquement par Django pour les erreurs HTTP
# 403.html : Accès refusé (Permission Denied)
# 404.html : Page non trouvée (Not Found)
# 500.html : Erreur serveur interne (Internal Server Error)
