from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_admin, name='dashboard_admin'),
    path('chauffeurs/', views.liste_chauffeurs, name='liste_chauffeurs'),
    path('recettes/', views.statistiques_recettes, name='statistiques_recettes'),
    path('pannes/', views.gestion_pannes, name='gestion_pannes'),
    path('classements/', views.classements, name='classements'),
]
