# =============================================================================
# CONFIGURATION DES URLS PRINCIPALES - Gaboma Driver Application
# =============================================================================
"""
Configuration des URLs principales pour l'application Gaboma Driver

Ce fichier centralise le routage de toutes les URLs de l'application :
- Interface d'administration Django
- Application des chauffeurs (drivers)
- Tableau de bord administrateur (admin_dashboard)
- Gestion des fichiers statiques en développement

Architecture des URLs :
- / : Application des chauffeurs (page d'accueil)
- /admin/ : Interface d'administration Django
- /admin-dashboard/ : Tableau de bord personnalisé pour les administrateurs
- /static/ : Fichiers statiques (CSS, JS, images)

L'application utilise un système de namespaces pour éviter les conflits
entre les URLs des différentes applications.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import de la configuration admin personnalisée
from admin_custom import *

# Import du webhook GitHub pour le déploiement automatique
from .webhook import github_webhook

# =============================================================================
# DÉFINITION DES ROUTES PRINCIPALES - Mapping des applications
# =============================================================================

urlpatterns = [
    # =============================================================================
    # INTERFACE D'ADMINISTRATION - Gestion des données
    # =============================================================================
    
    # Interface d'administration Django par défaut
    # Accès : /admin/
    # Utilisation : Gestion des chauffeurs, activités, pannes, etc.
    path('admin/', admin.site.urls),
    
    # =============================================================================
    # APPLICATION CHAUFFEURS - Interface principale des chauffeurs
    # =============================================================================
    
    # Application des chauffeurs (namespace: 'drivers')
    # Accès : / (racine)
    # Fonctionnalités : Connexion, dashboard, activités, etc.
    path('', include('drivers.urls')),
    
    # =============================================================================
    # TABLEAU DE BORD ADMINISTRATEUR - Interface personnalisée
    # =============================================================================
    
    # Tableau de bord administrateur personnalisé (namespace: 'admin_dashboard')
    # Accès : /admin-dashboard/
    # Fonctionnalités : Statistiques, rapports, gestion avancée
    path('admin-dashboard/', include('admin_dashboard.urls')),
    
    # =============================================================================
    # WEBHOOK GITHUB - Déploiement automatique
    # =============================================================================
    
    # Webhook GitHub pour déclencher le déploiement automatique
    # Accès : /webhook/github/
    # Utilisation : Configuré sur GitHub pour appeler cette URL lors d'un push
    path('webhook/github/', github_webhook, name='github_webhook'),
]

# =============================================================================
# CONFIGURATION DES FICHIERS STATIQUES - Développement uniquement
# =============================================================================

# Servir les fichiers statiques en mode développement
# En production, les fichiers statiques sont servis par le serveur web (Nginx, Apache)
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
