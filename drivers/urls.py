from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_chauffeur, name='login_chauffeur'),
    path('creer-compte/', views.creer_compte_chauffeur, name='creer_compte'),
    path('dashboard/', views.dashboard_chauffeur, name='dashboard_chauffeur'),
    path('prendre-cles/', views.prendre_cles, name='prendre_cles'),
    path('remettre-cles/', views.remettre_cles, name='remettre_cles'),
    path('signaler-panne/', views.signaler_panne, name='signaler_panne'),
    path('nouvelle-activite/', views.nouvelle_activite, name='nouvelle_activite'),
    path('exporter-pdf/', views.exporter_activite_pdf, name='exporter_pdf'),
    path('activite-mensuelle/', views.activite_mensuelle, name='activite_mensuelle'),
    path('demander-modification/', views.demander_modification, name='demander_modification'),
    path('mes-demandes/', views.mes_demandes, name='mes_demandes'),
    path('mon-compte/', views.mon_compte, name='mon_compte'),
]
