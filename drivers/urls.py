# =============================================================================
# CONFIGURATION DES URLS - Application Drivers
# =============================================================================
"""
Configuration des URLs pour l'application drivers de Gaboma Driver

Ce fichier définit toutes les routes (URLs) disponibles pour les chauffeurs :
- Pages d'accueil et d'authentification
- Dashboard et gestion des activités
- Fonctionnalités avancées (PDF, calendrier, modifications)

Structure des URLs :
- / : Page d'accueil
- /login/ : Connexion chauffeur
- /creer-compte/ : Création de compte
- /dashboard/ : Tableau de bord principal
- /prendre-cles/ : Prise de clés du matin
- /remettre-cles/ : Remise de clés du soir
- /nouvelle-activite/ : Sélection d'activité
- /exporter-pdf/ : Export PDF des activités
- /activite-mensuelle/ : Calendrier mensuel
- /demander-modification/ : Demande de modification
- /mes-demandes/ : Consultation des demandes
- /mon-compte/ : Gestion du compte
"""

from django.urls import path
from . import views

# Nom de l'application pour le namespace des URLs
app_name = 'drivers'

# =============================================================================
# DÉFINITION DES ROUTES - Mapping URL -> Vue
# =============================================================================

urlpatterns = [
    # =============================================================================
    # PAGES PUBLIQUES - Accessibles sans authentification
    # =============================================================================
    
    # Page d'accueil de l'application
    path('', views.index, name='index'),
    
    # Authentification des chauffeurs
    path('login/', views.login_chauffeur, name='login_chauffeur'),
    path('login-superviseur/', views.login_superviseur, name='login_superviseur'),
    path('creer-compte/', views.creer_compte_chauffeur, name='creer_compte'),
    
    # =============================================================================
    # DASHBOARD ET ACTIVITÉS - Pages principales des chauffeurs
    # =============================================================================
    
    # Tableau de bord principal du chauffeur
    path('dashboard/', views.dashboard_chauffeur, name='dashboard_chauffeur'),
    
    # Gestion des activités quotidiennes
    path('prendre-cles/', views.prendre_cles, name='prendre_cles'),
    path('remettre-cles/', views.remettre_cles, name='remettre_cles'),
    path('nouvelle-activite/', views.nouvelle_activite, name='nouvelle_activite'),
    
    # =============================================================================
    # FONCTIONNALITÉS AVANCÉES - Outils et rapports
    # =============================================================================
    
    # Export et partage
    path('exporter-pdf/', views.exporter_activite_pdf, name='exporter_pdf'),
    
    # Consultation des activités
    path('activite-mensuelle/', views.activite_mensuelle, name='activite_mensuelle'),
    
    # =============================================================================
    # GESTION DES MODIFICATIONS - Workflow d'approbation
    # =============================================================================
    
    # Demandes de modification d'activité
    path('demander-modification/', views.demander_modification, name='demander_modification'),
    path('mes-demandes/', views.mes_demandes, name='mes_demandes'),
    
    # =============================================================================
    # GESTION DU COMPTE - Paramètres personnels
    # =============================================================================
    
    # Gestion du compte chauffeur
    path('mon-compte/', views.mon_compte, name='mon_compte'),
    path('supprimer-compte/', views.supprimer_compte_chauffeur, name='supprimer_compte'),
    path('logout/', views.logout_chauffeur, name='logout_chauffeur'),
]
