from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from drivers.models import Chauffeur
from activities.models import Activite, Recette, Panne


@staff_member_required
def dashboard_admin(request):
    """Tableau de bord administrateur"""
    
    # Statistiques générales
    total_chauffeurs = Chauffeur.objects.filter(actif=True).count()
    total_activites_aujourdhui = Activite.objects.filter(
        date_heure__date=date.today()
    ).count()
    
    # Recettes
    recettes_aujourdhui = Recette.objects.filter(
        date=date.today()
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    recettes_semaine = Recette.objects.filter(
        date__gte=date.today() - timedelta(days=7)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    recettes_mois = Recette.objects.filter(
        date__gte=date.today().replace(day=1)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Pannes
    pannes_en_cours = Panne.objects.filter(statut='en_cours').count()
    pannes_critiques = Panne.objects.filter(severite='critique').count()
    
    # Top chauffeurs du mois
    top_chauffeurs_mois = Chauffeur.objects.filter(
        recette__date__gte=date.today().replace(day=1)
    ).annotate(
        total_recettes=Sum('recette__montant')
    ).order_by('-total_recettes')[:3]
    
    # Activités récentes
    activites_recentes = Activite.objects.select_related('chauffeur').order_by('-date_heure')[:10]
    
    # Pannes récentes
    pannes_recentes = Panne.objects.select_related('chauffeur').order_by('-date_creation')[:5]
    
    context = {
        'total_chauffeurs': total_chauffeurs,
        'total_activites_aujourdhui': total_activites_aujourdhui,
        'recettes_aujourdhui': recettes_aujourdhui,
        'recettes_semaine': recettes_semaine,
        'recettes_mois': recettes_mois,
        'pannes_en_cours': pannes_en_cours,
        'pannes_critiques': pannes_critiques,
        'top_chauffeurs_mois': top_chauffeurs_mois,
        'activites_recentes': activites_recentes,
        'pannes_recentes': pannes_recentes,
    }
    
    return render(request, 'admin_dashboard/dashboard.html', context)


@staff_member_required
def liste_chauffeurs(request):
    """Liste des chauffeurs"""
    chauffeurs = Chauffeur.objects.all().order_by('nom', 'prenom')
    
    context = {
        'chauffeurs': chauffeurs,
    }
    
    return render(request, 'admin_dashboard/liste_chauffeurs.html', context)


@staff_member_required
def statistiques_recettes(request):
    """Statistiques des recettes"""
    # Filtres de période
    periode = request.GET.get('periode', 'mois')
    
    if periode == 'jour':
        date_debut = date.today()
        date_fin = date.today()
    elif periode == 'semaine':
        date_debut = date.today() - timedelta(days=7)
        date_fin = date.today()
    elif periode == 'mois':
        date_debut = date.today().replace(day=1)
        date_fin = date.today()
    elif periode == 'annee':
        date_debut = date.today().replace(month=1, day=1)
        date_fin = date.today()
    else:
        date_debut = date.today().replace(day=1)
        date_fin = date.today()
    
    # Recettes par chauffeur
    recettes_chauffeurs = Chauffeur.objects.filter(
        recette__date__gte=date_debut,
        recette__date__lte=date_fin
    ).annotate(
        total_recettes=Sum('recette__montant'),
        nb_jours=Count('recette', distinct=True)
    ).order_by('-total_recettes')
    
    # Recettes par jour
    recettes_par_jour = Recette.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin
    ).values('date').annotate(
        total=Sum('montant')
    ).order_by('date')
    
    context = {
        'periode': periode,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'recettes_chauffeurs': recettes_chauffeurs,
        'recettes_par_jour': recettes_par_jour,
    }
    
    return render(request, 'admin_dashboard/statistiques_recettes.html', context)


@staff_member_required
def gestion_pannes(request):
    """Gestion des pannes"""
    pannes = Panne.objects.select_related('chauffeur').order_by('-date_creation')
    
    # Filtres
    statut = request.GET.get('statut')
    severite = request.GET.get('severite')
    
    if statut:
        pannes = pannes.filter(statut=statut)
    if severite:
        pannes = pannes.filter(severite=severite)
    
    context = {
        'pannes': pannes,
        'statut_actuel': statut,
        'severite_actuelle': severite,
    }
    
    return render(request, 'admin_dashboard/gestion_pannes.html', context)


@staff_member_required
def classements(request):
    """Classements et gamification"""
    
    # Top chauffeurs du jour
    top_jour = Chauffeur.objects.filter(
        recette__date=date.today()
    ).annotate(
        recette_jour=Sum('recette__montant')
    ).filter(recette_jour__gt=0).order_by('-recette_jour')[:3]
    
    # Top chauffeurs de la semaine
    semaine_debut = date.today() - timedelta(days=date.today().weekday())
    top_semaine = Chauffeur.objects.filter(
        recette__date__gte=semaine_debut
    ).annotate(
        recette_semaine=Sum('recette__montant')
    ).filter(recette_semaine__gt=0).order_by('-recette_semaine')[:3]
    
    # Top chauffeurs du mois
    mois_debut = date.today().replace(day=1)
    top_mois = Chauffeur.objects.filter(
        recette__date__gte=mois_debut
    ).annotate(
        recette_mois=Sum('recette__montant')
    ).filter(recette_mois__gt=0).order_by('-recette_mois')[:3]
    
    # Statistiques de présence
    presence_semaine = Chauffeur.objects.annotate(
        jours_travailles=Count('activite', filter=Q(
            activite__type_activite='prise',
            activite__date_heure__gte=semaine_debut
        ), distinct=True)
    ).order_by('-jours_travailles')
    
    context = {
        'top_jour': top_jour,
        'top_semaine': top_semaine,
        'top_mois': top_mois,
        'presence_semaine': presence_semaine,
    }
    
    return render(request, 'admin_dashboard/classements.html', context)