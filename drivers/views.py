from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
    print("Initiation de connexion...")
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"Tentative de connexion: username={username}")
        
        # Vérification basique des champs
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/login_chauffeur.html')
        
        # Authentification Django
        user = authenticate(request, username=username, password=password)
        print(f"Authentification: user={user}")
        
        if user is not None:
            try:
                # Vérifier si l'utilisateur correspond à un chauffeur
                chauffeur = Chauffeur.objects.get(user=user)
                print(f"Chauffeur trouvé: {chauffeur.nom} {chauffeur.prenom}, actif: {chauffeur.actif}")
                
                if chauffeur.actif:
                    # Connexion Django (met l'utilisateur en session)
                    login(request, user)
                    
                    # Message flash de bienvenue
                    messages.success(request, f'Bienvenue {chauffeur.prenom} {chauffeur.nom} !')
                    
                    # ✅ Redirection explicite vers le dashboard chauffeur
                    return redirect('drivers:dashboard_chauffeur')
                else:
                    messages.error(request, 'Votre compte chauffeur est désactivé.')
            
            except Chauffeur.DoesNotExist:
                print("Aucun chauffeur associé à ce compte")
                messages.error(request, 'Aucun chauffeur associé à ce compte.')
        else:
            print("Authentification échouée")
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    # Si GET ou erreur: on recharge le template login
    print(f"Fin de connexion: {request.method}")
    return render(request, 'drivers/login_chauffeur.html')


def creer_compte_chauffeur(request):
    """Création d'un compte chauffeur"""
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        print(f"Tentative de création: {username}")
        
        # Validation des champs
        if not all([nom, prenom, telephone, email, username, password, password_confirm]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/creer_compte.html')
        
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'drivers/creer_compte.html')
        
        if len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            return render(request, 'drivers/creer_compte.html')
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà utilisé.')
            return render(request, 'drivers/creer_compte.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cette adresse email est déjà utilisée.')
            return render(request, 'drivers/creer_compte.html')
        
        try:
            # Créer l'utilisateur Django
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=prenom,
                last_name=nom
            )
            
            # Créer le profil chauffeur lié
            chauffeur = Chauffeur.objects.create(
                user=user,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                actif=True
            )
            
            messages.success(request, f'Compte créé avec succès ! Bienvenue {prenom} {nom} !')
            
            # Authentifier puis connecter automatiquement l'utilisateur
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                
                # ✅ Redirection explicite vers le dashboard chauffeur
                return redirect('drivers:dashboard_chauffeur')
            
        except Exception as e:
            print(f"Erreur lors de la création: {e}")
            messages.error(request, 'Une erreur est survenue lors de la création du compte.')
    
    return render(request, 'drivers/creer_compte.html')


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
        return redirect('drivers:dashboard_chauffeur')
    
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
                return redirect('drivers:dashboard_chauffeur')
                
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
        return redirect('drivers:dashboard_chauffeur')
    
    # Vérifier si une remise a déjà été faite aujourd'hui
    if RemiseCles.objects.filter(chauffeur=chauffeur, date=today).exists():
        messages.warning(request, 'Vous avez déjà remis les clés aujourd\'hui.')
        return redirect('drivers:dashboard_chauffeur')
    
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
                
                # Calculer le message motivant (méthode à définir dans ton modèle RemiseCles)
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
                
                return redirect('drivers:dashboard_chauffeur')
                
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
        return redirect('drivers:dashboard_chauffeur')
    
    return render(request, 'drivers/signaler_panne.html', {'chauffeur': chauffeur})
