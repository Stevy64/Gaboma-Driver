from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, date, time
from .models import Chauffeur
from activities.models import Activite, Recette, Panne, PriseCles, RemiseCles


def index(request):
    """Page d'accueil avec choix de connexion"""
    return render(request, 'drivers/index.html')


def login_chauffeur(request):
    """Connexion des chauffeurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validation des champs
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/login_chauffeur.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                chauffeur = Chauffeur.objects.get(user=user)
                if chauffeur.actif:
                    login(request, user)
                    messages.success(request, f'✅ Connexion réussie ! Bienvenue {chauffeur.nom_complet}.')
                    return redirect('drivers:dashboard_chauffeur')
                else:
                    messages.error(request, '❌ Votre compte chauffeur est désactivé. Contactez l\'administrateur.')
            except Chauffeur.DoesNotExist:
                messages.error(request, '❌ Aucun chauffeur associé à ce compte. Contactez l\'administrateur.')
        else:
            messages.error(request, '❌ Nom d\'utilisateur ou mot de passe incorrect. Vérifiez vos identifiants.')
    
    return render(request, 'drivers/login_chauffeur.html')


@login_required
def dashboard_chauffeur(request):
    """Tableau de bord du chauffeur avec nouvelle logique"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    today = date.today()
    
    # Vérifier l'état actuel : prise et remise du jour
    prise_aujourdhui = PriseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    remise_aujourdhui = RemiseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    # Déterminer les actions possibles
    peut_prendre_cles = not prise_aujourdhui
    peut_remettre_cles = prise_aujourdhui and not remise_aujourdhui
    
    # Récupérer l'historique des 7 derniers jours
    week_start = today - timezone.timedelta(days=7)
    prises_recentes = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('-date')[:7]
    
    remises_recentes = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('-date')[:7]
    
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,
        'remise_aujourdhui': remise_aujourdhui,
        'peut_prendre_cles': peut_prendre_cles,
        'peut_remettre_cles': peut_remettre_cles,
        'prises_recentes': prises_recentes,
        'remises_recentes': remises_recentes,
    }
    
    return render(request, 'drivers/dashboard_chauffeur.html', context)


@login_required
def prendre_cles(request):
    """Formulaire de prise de clés du matin"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Vérifier si une prise a déjà été faite aujourd'hui
    today = date.today()
    if PriseCles.objects.filter(chauffeur=chauffeur, date=today).exists():
        messages.warning(request, 'Vous avez déjà pris les clés aujourd\'hui.')
        return redirect('dashboard_chauffeur')
    
    if request.method == 'POST':
        objectif_recette = request.POST.get('objectif_recette')
        plein_carburant = request.POST.get('plein_carburant') == 'on'
        probleme_mecanique = request.POST.get('probleme_mecanique', 'Aucun')
        signature = request.POST.get('signature', '')
        
        # Validation
        if not objectif_recette or not signature:
            messages.error(request, 'L\'objectif de recette et la signature sont obligatoires.')
        else:
            try:
                objectif_recette = int(objectif_recette)
                if objectif_recette <= 0:
                    raise ValueError()
                
                # Créer la prise de clés
                PriseCles.objects.create(
                    chauffeur=chauffeur,
                    date=today,
                    heure_prise=timezone.now().time(),
                    objectif_recette=objectif_recette,
                    plein_carburant=plein_carburant,
                    probleme_mecanique=probleme_mecanique,
                    signature=signature
                )
                
                messages.success(request, '✅ La journée peut commencer, bonne route !')
                return redirect('dashboard_chauffeur')
                
            except ValueError:
                messages.error(request, 'L\'objectif de recette doit être un nombre entier positif.')
    
    return render(request, 'drivers/prendre_cles.html', {'chauffeur': chauffeur, 'today': today})


@login_required
def remettre_cles(request):
    """Formulaire de remise de clés du soir"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    today = date.today()
    
    # Vérifier si une prise a été faite aujourd'hui
    prise_aujourdhui = PriseCles.objects.filter(chauffeur=chauffeur, date=today).first()
    if not prise_aujourdhui:
        messages.warning(request, 'Vous devez d\'abord prendre les clés avant de les remettre.')
        return redirect('dashboard_chauffeur')
    
    # Vérifier si une remise a déjà été faite aujourd'hui
    if RemiseCles.objects.filter(chauffeur=chauffeur, date=today).exists():
        messages.warning(request, 'Vous avez déjà remis les clés aujourd\'hui.')
        return redirect('dashboard_chauffeur')
    
    if request.method == 'POST':
        recette_realisee = request.POST.get('recette_realisee')
        plein_carburant = request.POST.get('plein_carburant') == 'on'
        probleme_mecanique = request.POST.get('probleme_mecanique', 'Aucun')
        signature = request.POST.get('signature', '')
        
        # Validation
        if not recette_realisee or not signature:
            messages.error(request, 'La recette réalisée et la signature sont obligatoires.')
        else:
            try:
                recette_realisee = int(recette_realisee)
                if recette_realisee < 0:
                    raise ValueError()
                
                # Créer la remise de clés
                remise = RemiseCles.objects.create(
                    chauffeur=chauffeur,
                    date=today,
                    heure_remise=timezone.now().time(),
                    recette_realisee=recette_realisee,
                    plein_carburant=plein_carburant,
                    probleme_mecanique=probleme_mecanique,
                    signature=signature
                )
                
                # Calculer le message motivant
                type_message, message_motivant = remise.get_objectif_atteint()
                
                # Ajouter le message avec le bon type
                if type_message == 'success':
                    messages.success(request, message_motivant)
                elif type_message == 'warning':
                    messages.warning(request, message_motivant)
                elif type_message == 'danger':
                    messages.error(request, message_motivant)
                else:
                    messages.info(request, message_motivant)
                
                return redirect('dashboard_chauffeur')
                
            except ValueError:
                messages.error(request, 'La recette réalisée doit être un nombre entier positif ou zéro.')
    
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,
    }
    return render(request, 'drivers/remettre_cles.html', context)


@login_required
def signaler_panne(request):
    """Formulaire de signalement de panne"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
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