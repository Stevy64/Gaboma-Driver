from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # =============================================================================
    # PAGES PRINCIPALES - Tableau de bord et fonctionnalités de base
    # =============================================================================
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('chauffeurs/', views.liste_chauffeurs, name='liste_chauffeurs'),
    path('recettes/', views.statistiques_recettes, name='statistiques_recettes'),
    path('recettes/excel/', views.exporter_excel, name='exporter_excel'),
    path('calendrier/', views.calendrier_activites, name='calendrier_activites'),
    path('pannes/', views.gestion_pannes, name='gestion_pannes'),
    path('classements/', views.classements, name='classements'),
    
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
]
