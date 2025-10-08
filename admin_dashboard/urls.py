from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # =============================================================================
    # PAGES PRINCIPALES - Tableau de bord et fonctionnalités de base
    # =============================================================================
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('superviseur/', views.dashboard_superviseur, name='dashboard_superviseur'),
    path('chauffeurs/', views.liste_chauffeurs, name='liste_chauffeurs'),
    path('recettes/', views.statistiques_recettes, name='statistiques_recettes'),
    path('recettes/excel/', views.exporter_excel, name='exporter_excel'),
    path('calendrier/', views.calendrier_activites, name='calendrier_activites'),
    path('pannes/', views.gestion_pannes, name='gestion_pannes'),
    
    # =============================================================================
    # GESTION DES ACTIVITÉS - Nouvelles fonctionnalités
    # =============================================================================
    path('activites/', views.gestion_activites, name='gestion_activites'),
    path('activites/chauffeur/<int:chauffeur_id>/', views.activites_chauffeur, name='activites_chauffeur'),
    path('activites/chauffeur/<int:chauffeur_id>/pdf/', views.exporter_activite_chauffeur_pdf, name='exporter_activite_chauffeur_pdf'),
    
    # =============================================================================
    # GESTION DES DEMANDES DE MODIFICATION - Workflow d'approbation
    # =============================================================================
    path('demandes-modification/', views.gestion_demandes_modification, name='gestion_demandes_modification'),
    path('demandes-modification/<int:demande_id>/traiter/', views.traiter_demande_modification, name='traiter_demande_modification'),
    
    # =============================================================================
    # FONCTIONNALITÉS DE SUPPRESSION - Gestion des données
    # =============================================================================
    path('supprimer-activite/<int:activite_id>/<str:type_activite>/', views.supprimer_activite, name='supprimer_activite'),
    path('supprimer-toutes-activites/', views.supprimer_toutes_activites, name='supprimer_toutes_activites'),
    path('supprimer-demande-modification/<int:demande_id>/', views.supprimer_demande_modification, name='supprimer_demande_modification'),
    path('reinitialiser-demandes-modification/', views.reinitialiser_demandes_modification, name='reinitialiser_demandes_modification'),
    path('supprimer-panne/<int:panne_id>/', views.supprimer_panne, name='supprimer_panne'),
    path('supprimer-toutes-pannes/', views.supprimer_toutes_pannes, name='supprimer_toutes_pannes'),
    
    # =============================================================================
    # GESTION DES SUPERVISEURS - Privilèges et permissions
    # =============================================================================
    path('superviseurs/', views.gestion_superviseurs, name='gestion_superviseurs'),
    path('superviseurs/ajouter/<int:user_id>/', views.ajouter_superviseur, name='ajouter_superviseur'),
    path('superviseurs/retirer/<int:user_id>/', views.retirer_superviseur, name='retirer_superviseur'),
    path('superviseurs/creer/', views.creer_superviseur, name='creer_superviseur'),
    path('superviseurs/assigner/<int:superviseur_id>/', views.assigner_chauffeurs, name='assigner_chauffeurs'),
    path('superviseurs/detail/<int:superviseur_id>/', views.detail_superviseur, name='detail_superviseur'),
    path('supprimer-compte-superviseur/', views.supprimer_compte_superviseur, name='supprimer_compte_superviseur'),
    
    path('logout/', views.logout_admin, name='logout_admin'),
]
