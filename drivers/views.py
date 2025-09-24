from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date
from .models import Chauffeur
from activities.models import Activite, Recette, Panne


def index(request):
    """Page d'accueil avec choix de connexion"""
    return render(request, 'drivers/index.html')


def login_chauffeur(request):
    """Connexion des chauffeurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                chauffeur = Chauffeur.objects.get(user=user)
                if chauffeur.actif:
                    login(request, user)
                    return redirect('dashboard_chauffeur')
                else:
                    messages.error(request, 'Votre compte chauffeur est désactivé.')
            except Chauffeur.DoesNotExist:
                messages.error(request, 'Aucun chauffeur associé à ce compte.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'drivers/login_chauffeur.html')


@login_required
def dashboard_chauffeur(request):
    """Tableau de bord du chauffeur"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('index')
    
    # Vérifier s'il y a une activité en cours
    activite_en_cours = Activite.objects.filter(
        chauffeur=chauffeur,
        type_activite='prise'
    ).exclude(
        id__in=Activite.objects.filter(
            chauffeur=chauffeur,
            type_activite='remise'
        ).values_list('id', flat=True)
    ).order_by('-date_heure').first()
    
    # Récupérer les activités récentes
    activites_recentes = Activite.objects.filter(
        chauffeur=chauffeur
    ).order_by('-date_heure')[:10]
    
    # Récupérer les recettes de la semaine
    today = date.today()
    week_start = today - timezone.timedelta(days=today.weekday())
    recettes_semaine = Recette.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('-date')
    
    context = {
        'chauffeur': chauffeur,
        'activite_en_cours': activite_en_cours,
        'activites_recentes': activites_recentes,
        'recettes_semaine': recettes_semaine,
    }
    
    return render(request, 'drivers/dashboard_chauffeur.html', context)


@login_required
def prise_cles(request):
    """Formulaire de prise de clés"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('index')
    
    if request.method == 'POST':
        carburant_litres = request.POST.get('carburant_litres')
        carburant_pourcentage = request.POST.get('carburant_pourcentage')
        signature = request.POST.get('signature', '')
        
        # Créer l'activité de prise de clés
        activite = Activite.objects.create(
            chauffeur=chauffeur,
            type_activite='prise',
            date_heure=timezone.now(),
            carburant_litres=carburant_litres if carburant_litres else None,
            carburant_pourcentage=carburant_pourcentage if carburant_pourcentage else None,
            signature=signature
        )
        
        messages.success(request, 'Prise de clés enregistrée avec succès!')
        return redirect('dashboard_chauffeur')
    
    return render(request, 'drivers/prise_cles.html', {'chauffeur': chauffeur})


@login_required
def remise_cles(request):
    """Formulaire de remise de clés"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('index')
    
    if request.method == 'POST':
        recette_jour = request.POST.get('recette_jour')
        etat_vehicule = request.POST.get('etat_vehicule', '')
        notes = request.POST.get('notes', '')
        signature = request.POST.get('signature', '')
        
        # Créer l'activité de remise de clés
        activite = Activite.objects.create(
            chauffeur=chauffeur,
            type_activite='remise',
            date_heure=timezone.now(),
            recette_jour=recette_jour if recette_jour else None,
            etat_vehicule=etat_vehicule,
            notes=notes,
            signature=signature
        )
        
        # Créer ou mettre à jour la recette du jour
        if recette_jour:
            recette, created = Recette.objects.get_or_create(
                chauffeur=chauffeur,
                date=date.today(),
                defaults={'montant': recette_jour}
            )
            if not created:
                recette.montant = recette_jour
                recette.save()
        
        messages.success(request, 'Remise de clés enregistrée avec succès!')
        return redirect('dashboard_chauffeur')
    
    return render(request, 'drivers/remise_cles.html', {'chauffeur': chauffeur})


@login_required
def signaler_panne(request):
    """Formulaire de signalement de panne"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('index')
    
    if request.method == 'POST':
        description = request.POST.get('description')
        severite = request.POST.get('severite', 'mineure')
        
        panne = Panne.objects.create(
            chauffeur=chauffeur,
            description=description,
            severite=severite
        )
        
        messages.success(request, 'Panne signalée avec succès!')
        return redirect('dashboard_chauffeur')
    
    return render(request, 'drivers/signaler_panne.html', {'chauffeur': chauffeur})