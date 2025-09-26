# =============================================================================
# IMPORTS - Importation des modules nécessaires
# =============================================================================

# Django core imports - Imports de base de Django
from django.shortcuts import render, redirect  # Rendu de templates et redirections
from django.contrib.auth import login, authenticate  # Authentification des utilisateurs
from django.contrib.auth.decorators import login_required  # Décorateur pour protéger les vues
from django.contrib.auth.models import User  # Modèle utilisateur Django
from django.contrib import messages  # Système de messages flash
from django.http import HttpResponse  # Réponses HTTP
from django.utils import timezone  # Gestion du temps et des fuseaux horaires
from django.template.loader import render_to_string  # Rendu de templates en chaîne

# Imports Python standard - Modules de la bibliothèque standard
from datetime import datetime, date, timedelta  # Gestion des dates et heures

# Imports locaux - Modèles de l'application
from .models import Chauffeur  # Modèle chauffeur de l'app drivers
from activities.models import PriseCles, RemiseCles, DemandeModification  # Modèles d'activités

# Import conditionnel de weasyprint - Gestion PDF
# weasyprint est une bibliothèque optionnelle pour la génération de PDF
try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


# =============================================================================
# VUE D'ACCUEIL - Page principale de l'application
# =============================================================================

def index(request):
    """
    Vue d'accueil de l'application Gaboma Drive
    
    Cette vue affiche la page d'accueil avec les options de connexion
    pour les chauffeurs et les administrateurs.
    
    Args:
        request: Objet HttpRequest contenant les données de la requête
        
    Returns:
        HttpResponse: Rendu du template index.html
    """
    return render(request, 'drivers/index.html')


# =============================================================================
# AUTHENTIFICATION - Gestion de la connexion des chauffeurs
# =============================================================================

def login_chauffeur(request):
    """
    Vue de connexion pour les chauffeurs
    
    Cette vue gère l'authentification des chauffeurs. Elle vérifie les identifiants,
    s'assure que le compte chauffeur existe et est actif, puis connecte l'utilisateur.
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de connexion ou redirection vers le dashboard
    """
    # Traitement du formulaire de connexion (méthode POST)
    if request.method == 'POST':
        # Récupération des données du formulaire
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Validation des champs obligatoires
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/login_chauffeur.html')
        
        # Authentification Django - Vérification des identifiants
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                # Récupération du profil chauffeur associé à l'utilisateur
                chauffeur = Chauffeur.objects.get(user=user)
                
                # Vérification que le compte chauffeur est actif
                if chauffeur.actif:
                    # Connexion de l'utilisateur (création de la session)
                    login(request, user)
                    messages.success(request, f'Bienvenue {chauffeur.prenom} {chauffeur.nom} !')
                    return redirect('drivers:dashboard_chauffeur')
                else:
                    messages.error(request, 'Votre compte chauffeur est désactivé.')
            
            except Chauffeur.DoesNotExist:
                messages.error(request, 'Aucun chauffeur associé à ce compte.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    # Affichage du formulaire de connexion (méthode GET ou en cas d'erreur)
    return render(request, 'drivers/login_chauffeur.html')


def creer_compte_chauffeur(request):
    """
    Vue de création de compte pour les chauffeurs
    
    Cette vue permet aux nouveaux chauffeurs de créer leur compte. Elle valide
    les données, vérifie l'unicité des identifiants, crée l'utilisateur Django
    et le profil chauffeur associé.
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de création de compte ou redirection vers le dashboard
    """
    # Traitement du formulaire de création de compte (méthode POST)
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validation des champs obligatoires
        if not all([nom, prenom, telephone, email, username, password, password_confirm]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/creer_compte.html')
        
        # Validation de la correspondance des mots de passe
        if password != password_confirm:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
            return render(request, 'drivers/creer_compte.html')
        
        # Validation de la longueur du mot de passe
        if len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
            return render(request, 'drivers/creer_compte.html')
        
        # Vérification de l'unicité du nom d'utilisateur
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur est déjà utilisé.')
            return render(request, 'drivers/creer_compte.html')
        
        # Vérification de l'unicité de l'email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Cette adresse email est déjà utilisée.')
            return render(request, 'drivers/creer_compte.html')
        
        try:
            # Création de l'utilisateur Django
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=prenom,
                last_name=nom
            )
            
            # Création du profil chauffeur associé
            chauffeur = Chauffeur.objects.create(
                user=user,
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                actif=True  # Le compte est actif par défaut
            )
            
            messages.success(request, f'Compte créé avec succès ! Bienvenue {prenom} {nom} !')
            
            # Connexion automatique du nouvel utilisateur
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('drivers:dashboard_chauffeur')
            
        except Exception as e:
            # Gestion des erreurs lors de la création
            messages.error(request, 'Une erreur est survenue lors de la création du compte.')
    
    # Affichage du formulaire de création de compte (méthode GET)
    return render(request, 'drivers/creer_compte.html')


# =============================================================================
# DASHBOARD CHAUFFEUR - Tableau de bord principal
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def dashboard_chauffeur(request):
    """
    Dashboard principal du chauffeur
    
    Cette vue affiche le tableau de bord avec les informations du jour,
    les activités récentes, les statistiques de la semaine et les actions possibles.
    
    Logique métier :
    - Nouvelle activité possible à partir de 3h du matin
    - Prise de clés : si aucune prise n'a été faite aujourd'hui
    - Remise de clés : si une prise a été faite mais pas de remise
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Rendu du template dashboard_chauffeur.html
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Date du jour pour les vérifications
    today = date.today()
    
    # Vérification de l'état actuel : prise et remise du jour
    prise_aujourdhui = PriseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    remise_aujourdhui = RemiseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    # Récupération de l'heure actuelle (fuseau horaire configuré)
    from django.utils import timezone
    now = timezone.now()
    current_hour = now.hour
    
    # Détermination des actions possibles selon la logique métier
    peut_prendre_cles = not prise_aujourdhui and current_hour >= 3  # Prise possible si pas de prise et après 3h
    peut_remettre_cles = prise_aujourdhui and not remise_aujourdhui  # Remise possible si prise faite mais pas de remise
    nouvelle_activite_possible = not prise_aujourdhui and current_hour >= 3  # Nouvelle activité possible après 3h
    
    # =============================================================================
    # RÉCUPÉRATION DES DONNÉES HISTORIQUES - Semaine courante
    # =============================================================================
    
    # Calcul du début et fin de la semaine courante (lundi à dimanche)
    # Trouver le lundi de la semaine courante
    days_since_monday = today.weekday()  # 0 = lundi, 6 = dimanche
    week_start = today - timezone.timedelta(days=days_since_monday)
    week_end = week_start + timezone.timedelta(days=6)
    
    # Récupération des prises de clés de la semaine courante uniquement
    prises_recentes = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start,
        date__lte=week_end
    ).order_by('-date')[:7]  # Limitation à 7 enregistrements
    
    # Récupération des remises de clés de la semaine courante uniquement
    remises_recentes = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start,
        date__lte=week_end
    ).order_by('-date')[:7]  # Limitation à 7 enregistrements
    
    # =============================================================================
    # CONSTRUCTION DE LA LISTE D'ACTIVITÉS RÉCENTES COMBINÉES
    # =============================================================================
    
    activites_recentes = []
    
    # Ajout des prises de clés à la liste des activités
    for prise in prises_recentes:
        activites_recentes.append({
            'date_heure': timezone.datetime.combine(prise.date, prise.heure_prise),
            'type_activite': 'prise',
            'objectif_recette': prise.objectif_recette,
            'plein_carburant': prise.plein_carburant,
            'probleme_mecanique': prise.probleme_mecanique,
        })
    
    # Ajout des remises de clés à la liste des activités
    for remise in remises_recentes:
        activites_recentes.append({
            'date_heure': timezone.datetime.combine(remise.date, remise.heure_remise),
            'type_activite': 'remise',
            'recette_realisee': remise.recette_realisee,
            'plein_carburant': remise.plein_carburant,
            'probleme_mecanique': remise.probleme_mecanique,
        })
    
    # Tri par date/heure décroissante (plus récent en premier)
    activites_recentes.sort(key=lambda x: x['date_heure'], reverse=True)
    
    # Pagination des activités récentes
    from django.core.paginator import Paginator
    paginator = Paginator(activites_recentes, 15)  # 15 activités par page
    page_number = request.GET.get('page')
    activites_page = paginator.get_page(page_number)
    
    # =============================================================================
    # CALCUL DES STATISTIQUES DE LA SEMAINE
    # =============================================================================
    
    # Récupération de toutes les remises de clés de la semaine courante uniquement
    recettes_semaine = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start,
        date__lte=week_end
    ).order_by('-date')
    
    # Calcul du total des recettes de la semaine
    total_semaine = sum(remise.recette_realisee for remise in recettes_semaine)
    
    # Calcul du nombre de jours travaillés (nombre de remises = nombre de jours travaillés)
    nombre_jours_travailles = recettes_semaine.count()
    
    # Calcul de la moyenne journalière (total / nombre de jours travaillés)
    # Éviter la division par zéro si aucun jour travaillé
    moyenne_semaine = total_semaine / nombre_jours_travailles if nombre_jours_travailles > 0 else 0
    
    # =============================================================================
    # PRÉPARATION DU CONTEXTE POUR LE TEMPLATE
    # =============================================================================
    
    context = {
        # Informations du chauffeur et de la date
        'chauffeur': chauffeur,
        'today': today,
        
        # État actuel du jour
        'prise_aujourdhui': prise_aujourdhui,
        'remise_aujourdhui': remise_aujourdhui,
        
        # Actions possibles (logique métier)
        'peut_prendre_cles': peut_prendre_cles,
        'peut_remettre_cles': peut_remettre_cles,
        'nouvelle_activite_possible': nouvelle_activite_possible,
        'current_hour': current_hour,
        
        # Données historiques
        'prises_recentes': prises_recentes,
        'remises_recentes': remises_recentes,
        'activites_recentes': activites_page,
        'activites_paginator': paginator,
        
        # Statistiques de la semaine
        'recettes_semaine': recettes_semaine,
        'total_semaine': total_semaine,
        'moyenne_semaine': moyenne_semaine,
        'nombre_jours_travailles': nombre_jours_travailles,
    }
    
    # Rendu du template avec le contexte
    return render(request, 'drivers/dashboard_chauffeur.html', context)


# =============================================================================
# GESTION DES CLÉS - Prise de clés du matin
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def prendre_cles(request):
    """
    Vue de prise de clés du matin
    
    Cette vue gère la prise de clés par le chauffeur le matin. Elle enregistre
    l'objectif de recette, l'état du carburant, les problèmes mécaniques
    et la signature électronique.
    
    Contraintes métier :
    - Une seule prise de clés par jour par chauffeur
    - Objectif de recette obligatoire et positif
    - Signature électronique obligatoire
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de prise de clés ou redirection vers le dashboard
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Date du jour pour les vérifications
    today = date.today()
    
    # Vérification qu'aucune prise de clés n'a déjà été effectuée aujourd'hui
    if PriseCles.objects.filter(chauffeur=chauffeur, date=today).exists():
        messages.warning(request, 'Vous avez déjà pris les clés aujourd\'hui.')
        return redirect('drivers:dashboard_chauffeur')
    
    # Traitement du formulaire de prise de clés (méthode POST)
    if request.method == 'POST':
        # Récupération des données du formulaire
        objectif_recette_str = request.POST.get('objectif_recette', '0')
        objectif_recette = int(float(objectif_recette_str))  # Conversion en entier
        plein_carburant = request.POST.get('plein_carburant') == 'on'  # Checkbox
        probleme_mecanique = request.POST.get('probleme_mecanique', 'Aucun')
        signature = request.POST.get('signature', '')
        
        # Validation des champs obligatoires
        if not objectif_recette or not signature:
            messages.error(request, 'L\'objectif de recette et la signature sont obligatoires.')
        else:
            try:
                # Nettoyage et validation de l'objectif de recette
                objectif_recette_clean = str(objectif_recette).strip()
                objectif_recette = int(objectif_recette_clean)
                
                # Vérification que l'objectif est positif
                if objectif_recette <= 0:
                    raise ValueError()
                
                # Création de l'enregistrement de prise de clés
                prise_cles = PriseCles.objects.create(
                    chauffeur=chauffeur,
                    date=today,
                    heure_prise=timezone.now().time(),  # Heure actuelle
                    objectif_recette=objectif_recette,
                    plein_carburant=plein_carburant,
                    probleme_mecanique=probleme_mecanique,
                    signature=signature
                )
                
                # Création d'une panne si un problème mécanique est signalé
                if probleme_mecanique and probleme_mecanique != 'Aucun':
                    from activities.models import Panne
                    Panne.objects.create(
                        chauffeur=chauffeur,
                        description=probleme_mecanique,
                        date_signalement=today,
                        severite='moyenne',  # Par défaut
                        resolue=False
                    )
                
                # Message de succès avec emoji pour la motivation
                messages.success(request, '✅ La journée peut commencer, bonne route !')
                return redirect('drivers:dashboard_chauffeur')
                
            except ValueError:
                messages.error(request, 'L\'objectif de recette doit être un nombre entier positif.')
    
    # Affichage du formulaire de prise de clés (méthode GET)
    return render(request, 'drivers/prendre_cles.html', {'chauffeur': chauffeur, 'today': today})


@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def remettre_cles(request):
    """
    Vue de remise de clés du soir
    
    Cette vue gère la remise de clés par le chauffeur le soir. Elle enregistre
    la recette réalisée, l'état du carburant, les problèmes mécaniques
    et la signature électronique. Elle calcule également la performance
    par rapport à l'objectif fixé le matin.
    
    Contraintes métier :
    - Une prise de clés doit avoir été effectuée avant la remise
    - Une seule remise de clés par jour par chauffeur
    - Recette réalisée obligatoire (peut être zéro)
    - Signature électronique obligatoire
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de remise de clés ou redirection vers le dashboard
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Date du jour pour les vérifications
    today = date.today()
    
    # Vérification qu'une prise de clés a été effectuée aujourd'hui
    prise_aujourdhui = PriseCles.objects.filter(chauffeur=chauffeur, date=today).first()
    if not prise_aujourdhui:
        messages.warning(request, 'Vous devez d\'abord prendre les clés avant de les remettre.')
        return redirect('drivers:dashboard_chauffeur')
    
    # Vérification qu'aucune remise de clés n'a déjà été effectuée aujourd'hui
    if RemiseCles.objects.filter(chauffeur=chauffeur, date=today).exists():
        messages.warning(request, 'Vous avez déjà remis les clés aujourd\'hui.')
        return redirect('drivers:dashboard_chauffeur')
    
    # Traitement du formulaire de remise de clés (méthode POST)
    if request.method == 'POST':
        # Récupération des données du formulaire
        recette_realisee_str = request.POST.get('recette_realisee', '0')
        recette_realisee = int(float(recette_realisee_str))  # Conversion en entier
        plein_carburant = request.POST.get('plein_carburant') == 'on'  # Checkbox
        probleme_mecanique = request.POST.get('probleme_mecanique', 'Aucun')
        signature = request.POST.get('signature', '')
        
        # Validation des champs obligatoires
        if not recette_realisee or not signature:
            messages.error(request, 'La recette réalisée et la signature sont obligatoires.')
        else:
            try:
                # Nettoyage et validation de la recette réalisée
                recette_realisee = int(recette_realisee)
                
                # Vérification que la recette n'est pas négative
                if recette_realisee < 0:
                    raise ValueError()
                
                # Création de l'enregistrement de remise de clés
                remise = RemiseCles.objects.create(
                    chauffeur=chauffeur,
                    date=today,
                    heure_remise=timezone.now().time(),  # Heure actuelle
                    recette_realisee=recette_realisee,
                    plein_carburant=plein_carburant,
                    probleme_mecanique=probleme_mecanique,
                    signature=signature
                )
                
                # Création d'une panne si un problème mécanique est signalé
                if probleme_mecanique and probleme_mecanique != 'Aucun':
                    from activities.models import Panne
                    Panne.objects.create(
                        chauffeur=chauffeur,
                        description=probleme_mecanique,
                        date_signalement=today,
                        severite='moyenne',  # Par défaut
                        resolue=False
                    )
                
                # Calcul du message motivant basé sur la performance
                # La méthode get_objectif_atteint() compare la recette avec l'objectif
                type_message, message_motivant = remise.get_objectif_atteint()
                
                # Affichage du message selon le type (success, warning, danger, info)
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
    
    # Préparation du contexte pour le template
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,  # Pour afficher l'objectif dans le template
    }
    
    # Affichage du formulaire de remise de clés (méthode GET)
    return render(request, 'drivers/remettre_cles.html', context)


# =============================================================================
# NOUVELLE ACTIVITÉ - Sélection du type d'activité
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def nouvelle_activite(request):
    """
    Vue de sélection du type d'activité à créer
    
    Cette vue affiche les options disponibles pour créer une nouvelle activité :
    - Prise de clés (si possible)
    - Remise de clés (si possible)
    - Voir l'activité mensuelle
    
    La logique détermine quelles actions sont possibles selon l'état actuel
    de l'activité du jour.
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Rendu du template nouvelle_activite.html
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Date du jour pour les vérifications
    today = date.today()
    
    # Vérification de l'état actuel des activités du jour
    prise_aujourdhui = PriseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    remise_aujourdhui = RemiseCles.objects.filter(
        chauffeur=chauffeur, 
        date=today
    ).first()
    
    # Détermination des actions possibles selon la logique métier
    peut_prendre_cles = not prise_aujourdhui  # Prise possible si aucune prise n'a été faite
    peut_remettre_cles = prise_aujourdhui and not remise_aujourdhui  # Remise possible si prise faite mais pas de remise
    
    # Préparation du contexte pour le template
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,
        'remise_aujourdhui': remise_aujourdhui,
        'peut_prendre_cles': peut_prendre_cles,
        'peut_remettre_cles': peut_remettre_cles,
    }
    
    # Affichage de la page de sélection d'activité
    return render(request, 'drivers/nouvelle_activite.html', context)


# =============================================================================
# EXPORT PDF - Génération de rapport PDF de la semaine
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def exporter_activite_pdf(request):
    """
    Vue d'export PDF de l'activité de la semaine
    
    Cette vue génère un rapport PDF contenant l'activité de la semaine du chauffeur :
    - Résumé des 7 derniers jours
    - Détail jour par jour (prise/remise, recettes, objectifs)
    - Statistiques (total, moyenne, jours travaillés)
    - Pannes signalées (si disponibles)
    
    Prérequis : weasyprint doit être installé pour la génération PDF
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Fichier PDF en téléchargement ou redirection en cas d'erreur
    """
    # Vérification de la disponibilité de weasyprint
    if not WEASYPRINT_AVAILABLE:
        messages.error(request, 'La génération de PDF n\'est pas disponible. Veuillez installer weasyprint.')
        return redirect('drivers:dashboard_chauffeur')
    
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # =============================================================================
    # RÉCUPÉRATION DES DONNÉES DE LA SEMAINE
    # =============================================================================
    
    # Calcul de la période de la semaine (7 jours incluant aujourd'hui)
    today = date.today()
    week_start = today - timedelta(days=6)
    
    # Récupération des prises de clés de la semaine
    prises_semaine = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('date')
    
    # Récupération des remises de clés de la semaine
    remises_semaine = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('date')
    
    # Récupération des pannes de la semaine (si le modèle existe)
    try:
        from activities.models import Panne
        pannes_semaine = Panne.objects.filter(
            chauffeur=chauffeur,
            date_creation__gte=week_start
        ).order_by('date_creation')
    except ImportError:
        pannes_semaine = []  # Pas de pannes si le modèle n'existe pas
    
    # =============================================================================
    # CALCUL DES STATISTIQUES
    # =============================================================================
    
    # Calcul du total des recettes de la semaine
    total_recettes = sum(remise.recette_realisee for remise in remises_semaine)
    
    # Calcul de la moyenne journalière (total / 7 jours)
    moyenne_journaliere = total_recettes / 7 if remises_semaine.count() > 0 else 0
    
    # Calcul du nombre de jours travaillés (nombre de remises)
    jours_travailles = remises_semaine.count()
    
    # =============================================================================
    # CONSTRUCTION DU CALENDRIER DE LA SEMAINE
    # =============================================================================
    
    jours_semaine = []
    for i in range(7):
        # Calcul de la date du jour
        jour_date = week_start + timedelta(days=i)
        
        # Nom du jour de la semaine
        jour_nom = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][jour_date.weekday()]
        
        # Récupération des activités pour ce jour
        prise_jour = prises_semaine.filter(date=jour_date).first()
        remise_jour = remises_semaine.filter(date=jour_date).first()
        
        # Construction des données du jour
        jours_semaine.append({
            'date': jour_date,
            'nom': jour_nom,
            'prise': prise_jour,
            'remise': remise_jour,
            'recette': remise_jour.recette_realisee if remise_jour else 0,
            'objectif': prise_jour.objectif_recette if prise_jour else 0,
        })
    
    # =============================================================================
    # PRÉPARATION DU CONTEXTE POUR LE TEMPLATE PDF
    # =============================================================================
    
    context = {
        'chauffeur': chauffeur,
        'semaine_debut': week_start,
        'semaine_fin': today,
        'jours_semaine': jours_semaine,
        'prises_semaine': prises_semaine,
        'remises_semaine': remises_semaine,
        'pannes_semaine': pannes_semaine,
        'total_recettes': total_recettes,
        'moyenne_journaliere': moyenne_journaliere,
        'jours_travailles': jours_travailles,
        'date_generation': timezone.now(),
    }
    
    # =============================================================================
    # GÉNÉRATION DU PDF
    # =============================================================================
    
    # Rendu du template HTML en chaîne de caractères
    html_string = render_to_string('drivers/rapport_semaine_pdf.html', context)
    
    # Conversion HTML vers PDF avec weasyprint
    # base_url permet de résoudre les URLs relatives (CSS, images)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    # Création de la réponse HTTP avec le PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"rapport_semaine_{chauffeur.nom}_{today.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# =============================================================================
# ACTIVITÉ MENSUELLE - Calendrier et statistiques mensuelles
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def activite_mensuelle(request):
    """
    Vue d'activité mensuelle avec calendrier
    
    Cette vue affiche l'activité du chauffeur sous forme de calendrier mensuel
    avec les statistiques détaillées. Elle permet de naviguer entre les mois
    et les années pour consulter l'historique.
    
    Fonctionnalités :
    - Calendrier mensuel avec activités jour par jour
    - Statistiques du mois (total, moyenne, jours travaillés)
    - Statistiques de l'année
    - Navigation entre mois/années
    
    Args:
        request: Objet HttpRequest avec paramètres GET (mois, annee)
        
    Returns:
        HttpResponse: Rendu du template activite_mensuelle.html
    """
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Récupérer le mois et l'année depuis les paramètres GET
    today = date.today()
    annee = int(request.GET.get('annee', today.year))
    mois = int(request.GET.get('mois', today.month))
    
    # Calculer les dates de début et fin du mois
    mois_debut = date(annee, mois, 1)
    if mois == 12:
        mois_fin = date(annee + 1, 1, 1) - timedelta(days=1)
    else:
        mois_fin = date(annee, mois + 1, 1) - timedelta(days=1)
    
    # Récupérer les données du mois
    prises_mois = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=mois_debut,
        date__lte=mois_fin
    ).order_by('date')
    
    remises_mois = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=mois_debut,
        date__lte=mois_fin
    ).order_by('date')
    
    # Créer le calendrier du mois
    calendrier = creer_calendrier_mensuel(annee, mois, prises_mois, remises_mois)
    
    # Calculer les statistiques du mois
    total_mois = sum(remise.recette_realisee for remise in remises_mois)
    jours_travailles = remises_mois.count()
    moyenne_journaliere = total_mois / jours_travailles if jours_travailles > 0 else 0
    
    # Statistiques annuelles
    annee_debut = date(annee, 1, 1)
    annee_fin = date(annee, 12, 31)
    
    remises_annee = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=annee_debut,
        date__lte=annee_fin
    )
    
    total_annee = sum(remise.recette_realisee for remise in remises_annee)
    mois_travailles = remises_annee.values('date__month').distinct().count()
    
    # Calculer les recettes du jour, de la semaine en cours et du mois
    # Recette du jour (aujourd'hui)
    recette_jour = 0
    remise_aujourdhui = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date=today
    ).first()
    if remise_aujourdhui:
        recette_jour = remise_aujourdhui.recette_realisee
    
    # Calculer la semaine en cours (lundi à dimanche)
    # Trouver le lundi de la semaine en cours
    jours_semaine = today.weekday()  # 0 = lundi, 6 = dimanche
    lundi_semaine = today - timedelta(days=jours_semaine)
    dimanche_semaine = lundi_semaine + timedelta(days=6)
    
    # Recette de la semaine en cours
    remises_semaine = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=lundi_semaine,
        date__lte=dimanche_semaine
    )
    recette_semaine = sum(remise.recette_realisee for remise in remises_semaine)
    jours_travailles_semaine = remises_semaine.count()
    moyenne_semaine = recette_semaine / jours_travailles_semaine if jours_travailles_semaine > 0 else 0
    
    # Calculer la performance de la semaine
    # Récupérer les objectifs de la semaine
    prises_semaine = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=lundi_semaine,
        date__lte=dimanche_semaine
    )
    objectif_semaine = sum(prise.objectif_recette for prise in prises_semaine)
    performance_semaine = (recette_semaine / objectif_semaine * 100) if objectif_semaine > 0 else 0
    
    # Statistiques par mois de l'année
    stats_par_mois = []
    for m in range(1, 13):
        mois_debut_m = date(annee, m, 1)
        if m == 12:
            mois_fin_m = date(annee + 1, 1, 1) - timedelta(days=1)
        else:
            mois_fin_m = date(annee, m + 1, 1) - timedelta(days=1)
        
        remises_m = remises_annee.filter(date__gte=mois_debut_m, date__lte=mois_fin_m)
        total_m = sum(remise.recette_realisee for remise in remises_m)
        jours_m = remises_m.count()
        
        stats_par_mois.append({
            'mois': m,
            'nom_mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                         'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][m-1],
            'total': total_m,
            'jours': jours_m,
            'moyenne': total_m / jours_m if jours_m > 0 else 0,
            'actif': jours_m > 0
        })
    
    context = {
        'chauffeur': chauffeur,
        'annee': annee,
        'mois': mois,
        'mois_debut': mois_debut,
        'mois_fin': mois_fin,
        'calendrier': calendrier,
        'prises_mois': prises_mois,
        'remises_mois': remises_mois,
        'total_mois': total_mois,
        'jours_travailles': jours_travailles,
        'moyenne_journaliere': moyenne_journaliere,
        'total_annee': total_annee,
        'mois_travailles': mois_travailles,
        'stats_par_mois': stats_par_mois,
        'mois_nom': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][mois-1],
        # Nouvelles variables pour les recettes hebdomadaires et journalières
        'recette_jour': recette_jour,
        'recette_semaine': recette_semaine,
        'jours_travailles_semaine': jours_travailles_semaine,
        'moyenne_semaine': moyenne_semaine,
        'performance_semaine': performance_semaine,
        'semaine_debut': lundi_semaine,
        'semaine_fin': dimanche_semaine,
        'today': today,
    }
    
    return render(request, 'drivers/activite_mensuelle.html', context)


# =============================================================================
# FONCTIONS UTILITAIRES - Fonctions d'aide pour les vues
# =============================================================================

def creer_calendrier_mensuel(annee, mois, prises, remises):
    """
    Créer un calendrier mensuel avec les données d'activité
    
    Cette fonction utilitaire génère un calendrier mensuel structuré
    avec les activités (prises et remises de clés) pour chaque jour.
    Elle calcule également les performances et l'état de complétude.
    
    Args:
        annee (int): Année du calendrier
        mois (int): Mois du calendrier (1-12)
        prises (QuerySet): Prises de clés du mois
        remises (QuerySet): Remises de clés du mois
        
    Returns:
        list: Liste des semaines, chaque semaine contient une liste de jours
              avec les activités associées et les métadonnées
    """
    import calendar
    
    # Création du calendrier du mois avec le module calendar
    cal = calendar.monthcalendar(annee, mois)
    
    # Création de dictionnaires pour un accès rapide aux données
    # Optimisation : évite de refaire des requêtes dans la boucle
    prises_dict = {prise.date: prise for prise in prises}
    remises_dict = {remise.date: remise for remise in remises}
    
    # Construction de la structure de données pour le template
    calendrier_semaines = []
    
    for semaine in cal:
        semaine_data = []
        for jour in semaine:
            if jour == 0:  # Jour vide (hors du mois)
                semaine_data.append(None)
            else:
                # Création de la date du jour
                jour_date = date(annee, mois, jour)
                
                # Récupération des activités pour ce jour
                prise = prises_dict.get(jour_date)
                remise = remises_dict.get(jour_date)
                
                # Construction des données du jour
                jour_data = {
                    'jour': jour,
                    'date': jour_date,
                    'prise': prise,
                    'remise': remise,
                    'recette': remise.recette_realisee if remise else 0,
                    'objectif': prise.objectif_recette if prise else 0,
                    'actif': prise is not None or remise is not None,  # Au moins une activité
                    'complet': prise is not None and remise is not None,  # Prise ET remise
                }
                
                # Calcul du pourcentage de performance
                # Performance = (recette réalisée / objectif) * 100
                if jour_data['objectif'] > 0 and jour_data['recette'] > 0:
                    jour_data['performance'] = int((jour_data['recette'] / jour_data['objectif']) * 100)
                else:
                    jour_data['performance'] = 0
                
                semaine_data.append(jour_data)
        
        calendrier_semaines.append(semaine_data)
    
    return calendrier_semaines


# =============================================================================
# DEMANDES DE MODIFICATION - Gestion des demandes de modification d'activité
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def demander_modification(request):
    """
    Vue de demande de modification d'activité
    
    Cette vue permet aux chauffeurs de demander la modification d'une activité
    (prise ou remise de clés) déjà enregistrée. La demande doit être approuvée
    par un administrateur avant d'être appliquée.
    
    Processus :
    1. Sélection du type d'activité et de la date
    2. Saisie des nouvelles données
    3. Justification de la demande
    4. Création de la demande en attente d'approbation
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de demande de modification ou redirection
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    if request.method == 'POST':
        type_activite = request.POST.get('type_activite')
        date_activite_str = request.POST.get('date_activite')
        raison = request.POST.get('raison')
        
        if not all([type_activite, date_activite_str, raison]):
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/demander_modification.html')
        
        try:
            date_activite = datetime.strptime(date_activite_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Format de date invalide.')
            return render(request, 'drivers/demander_modification.html')
        
        # Récupérer l'activité existante
        if type_activite == 'prise':
            activite = PriseCles.objects.filter(chauffeur=chauffeur, date=date_activite).first()
        else:
            activite = RemiseCles.objects.filter(chauffeur=chauffeur, date=date_activite).first()
        
        if not activite:
            messages.error(request, 'Aucune activité trouvée pour cette date.')
            return render(request, 'drivers/demander_modification.html')
        
        donnees_originales = {}
        nouvelles_donnees = {}
        
        if type_activite == 'prise':
            donnees_originales = {
                'objectif_recette': activite.objectif_recette,
                'plein_carburant': activite.plein_carburant,
                'probleme_mecanique': activite.probleme_mecanique,
            }
            nouvelles_donnees = {
                'objectif_recette': int(float(request.POST.get('nouveau_objectif_recette', 0))),
                'plein_carburant': request.POST.get('nouveau_plein_carburant') == 'on',
                'probleme_mecanique': request.POST.get('nouveau_probleme_mecanique', ''),
            }
        else:
            donnees_originales = {
                'recette_realisee': activite.recette_realisee,
                'plein_carburant': activite.plein_carburant,
                'probleme_mecanique': activite.probleme_mecanique,
            }
            nouvelles_donnees = {
                'recette_realisee': int(float(request.POST.get('nouveau_recette_realisee', 0))),
                'plein_carburant': request.POST.get('nouveau_plein_carburant') == 'on',
                'probleme_mecanique': request.POST.get('nouveau_probleme_mecanique', ''),
            }
        
        from activities.models import DemandeModification
        demande = DemandeModification.objects.create(
            chauffeur=chauffeur,
            type_activite=type_activite,
            date_activite=date_activite,
            donnees_originales=donnees_originales,
            nouvelles_donnees=nouvelles_donnees,
            raison=raison
        )
        
        messages.success(request, 'Votre demande de modification a été envoyée à l\'administrateur.')
        return redirect('drivers:dashboard_chauffeur')
    
    # Récupérer les activités récentes pour le formulaire
    today = date.today()
    prises_recentes = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=today - timedelta(days=30)
    ).order_by('-date')[:10]
    
    remises_recentes = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=today - timedelta(days=30)
    ).order_by('-date')[:10]
    
    context = {
        'prises_recentes': prises_recentes,
        'remises_recentes': remises_recentes,
    }
    
    return render(request, 'drivers/demander_modification.html', context)


@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def mes_demandes(request):
    """
    Vue de consultation des demandes de modification
    
    Cette vue affiche toutes les demandes de modification du chauffeur connecté
    avec leur statut (en attente, approuvée, rejetée) et les détails de chaque demande.
    
    Fonctionnalités :
    - Liste chronologique des demandes
    - Statut de chaque demande
    - Détails des modifications demandées
    - Commentaires de l'administrateur
    
    Args:
        request: Objet HttpRequest de l'utilisateur connecté
        
    Returns:
        HttpResponse: Rendu du template mes_demandes.html
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    # Récupération de toutes les demandes du chauffeur, triées par date de création (plus récentes en premier)
    from activities.models import DemandeModification
    from django.core.paginator import Paginator
    
    demandes = DemandeModification.objects.filter(
        chauffeur=chauffeur
    ).order_by('-date_creation')
    
    # Pagination des demandes
    paginator = Paginator(demandes, 15)  # 15 demandes par page
    page_number = request.GET.get('page')
    demandes_page = paginator.get_page(page_number)
    
    # Préparation du contexte pour le template
    context = {
        'demandes': demandes_page,
        'demandes_paginator': paginator,
    }
    
    # Affichage de la liste des demandes
    return render(request, 'drivers/mes_demandes.html', context)


# =============================================================================
# GESTION DU COMPTE - Modification des informations personnelles
# =============================================================================

@login_required  # Décorateur : seuls les utilisateurs connectés peuvent accéder
def mon_compte(request):
    """
    Vue de gestion du compte chauffeur
    
    Cette vue permet aux chauffeurs de modifier leurs informations personnelles :
    - Nom et prénom
    - Numéro de téléphone
    - Adresse email
    - Mot de passe (optionnel)
    
    Les modifications sont appliquées à la fois sur le profil chauffeur
    et sur le compte utilisateur Django associé.
    
    Args:
        request: Objet HttpRequest contenant les données du formulaire
        
    Returns:
        HttpResponse: Template de gestion de compte ou redirection
    """
    # Récupération du profil chauffeur de l'utilisateur connecté
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        email = request.POST.get('email', '').strip()
        nouveau_password = request.POST.get('nouveau_password', '').strip()
        confirmer_password = request.POST.get('confirmer_password', '').strip()
        
        if not all([nom, prenom, telephone, email]):
            messages.error(request, 'Veuillez remplir tous les champs obligatoires.')
            return render(request, 'drivers/mon_compte.html', {'chauffeur': chauffeur})
        
        if '@' not in email or '.' not in email.split('@')[1]:
            messages.error(request, 'Veuillez saisir une adresse email valide.')
            return render(request, 'drivers/mon_compte.html', {'chauffeur': chauffeur})
        
        if len(telephone) < 8:
            messages.error(request, 'Le numéro de téléphone doit contenir au moins 8 chiffres.')
            return render(request, 'drivers/mon_compte.html', {'chauffeur': chauffeur})
        
        chauffeur.nom = nom
        chauffeur.prenom = prenom
        chauffeur.telephone = telephone
        chauffeur.email = email
        chauffeur.save()
        
        user = chauffeur.user
        user.email = email
        user.first_name = prenom
        user.last_name = nom
        user.save()
        
        if nouveau_password:
            if len(nouveau_password) < 6:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
                return render(request, 'drivers/mon_compte.html', {'chauffeur': chauffeur})
            
            if nouveau_password != confirmer_password:
                messages.error(request, 'Les mots de passe ne correspondent pas.')
                return render(request, 'drivers/mon_compte.html', {'chauffeur': chauffeur})
            
            # Changer le mot de passe
            user.set_password(nouveau_password)
            user.save()
            
            # Reconnecter l'utilisateur avec le nouveau mot de passe
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, 'Vos informations et votre mot de passe ont été mis à jour avec succès.')
        else:
            messages.success(request, 'Vos informations ont été mises à jour avec succès.')
        
        return redirect('drivers:dashboard_chauffeur')
    
    context = {
        'chauffeur': chauffeur,
    }
    
    return render(request, 'drivers/mon_compte.html', context)
