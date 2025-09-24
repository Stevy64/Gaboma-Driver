from django.urls import path
from . import views

app_name = 'drivers'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_chauffeur, name='login_chauffeur'),
    path('dashboard/', views.dashboard_chauffeur, name='dashboard_chauffeur'),
    path('prise-cles/', views.prise_cles, name='prise_cles'),
    path('remise-cles/', views.remise_cles, name='remise_cles'),
    path('signaler-panne/', views.signaler_panne, name='signaler_panne'),
]
