from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, date, time, timedelta
from .models import Chauffeur
from activities.models import PriseCles, RemiseCles
from django.template.loader import render_to_string
import weasyprint


def index(request):
    """Page d'accueil avec choix de connexion"""
    return render(request, 'drivers/index.html')


def login_chauffeur(request):
    """Connexion des chauffeurs"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Vérification basique des champs
        if not username or not password:
            messages.error(request, 'Veuillez remplir tous les champs.')
            return render(request, 'drivers/login_chauffeur.html')
        
        # Authentification Django
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            try:
                # Vérifier si l'utilisateur correspond à un chauffeur
                chauffeur = Chauffeur.objects.get(user=user)
                
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
                messages.error(request, 'Aucun chauffeur associé à ce compte.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    # Si GET ou erreur: on recharge le template login
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
    
    # Créer une liste d'activités récentes combinées
    activites_recentes = []
    
    # Ajouter les prises récentes
    for prise in prises_recentes:
        activites_recentes.append({
            'date_heure': timezone.datetime.combine(prise.date, prise.heure_prise),
            'type_activite': 'prise',
            'objectif_recette': prise.objectif_recette,
            'plein_carburant': prise.plein_carburant,
            'probleme_mecanique': prise.probleme_mecanique,
        })
    
    # Ajouter les remises récentes
    for remise in remises_recentes:
        activites_recentes.append({
            'date_heure': timezone.datetime.combine(remise.date, remise.heure_remise),
            'type_activite': 'remise',
            'recette_realisee': remise.recette_realisee,
            'plein_carburant': remise.plein_carburant,
            'probleme_mecanique': remise.probleme_mecanique,
        })
    
    # Trier par date/heure décroissante
    activites_recentes.sort(key=lambda x: x['date_heure'], reverse=True)
    activites_recentes = activites_recentes[:10]  # Limiter à 10 activités
    
    # Récupérer les recettes de la semaine (7 derniers jours)
    recettes_semaine = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('-date')
    
    # Calculer les statistiques de la semaine
    total_semaine = sum(remise.recette_realisee for remise in recettes_semaine)
    moyenne_semaine = total_semaine / 7 if recettes_semaine.count() > 0 else 0
    
    
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,
        'remise_aujourdhui': remise_aujourdhui,
        'peut_prendre_cles': peut_prendre_cles,
        'peut_remettre_cles': peut_remettre_cles,
        'prises_recentes': prises_recentes,
        'remises_recentes': remises_recentes,
        'activites_recentes': activites_recentes,
        'recettes_semaine': recettes_semaine,
        'total_semaine': total_semaine,
        'moyenne_semaine': moyenne_semaine,
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
        objectif_recette_str = request.POST.get('objectif_recette', '0')
        objectif_recette = int(float(objectif_recette_str))
        plein_carburant = request.POST.get('plein_carburant') == 'on'
        probleme_mecanique = request.POST.get('probleme_mecanique', 'Aucun')
        signature = request.POST.get('signature', '')
        
        # Validation
        if not objectif_recette or not signature:
            messages.error(request, 'L\'objectif de recette et la signature sont obligatoires.')
        else:
            try:
                # Nettoyer la valeur (supprimer les espaces)
                objectif_recette_clean = str(objectif_recette).strip()
                objectif_recette = int(objectif_recette_clean)
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
        recette_realisee_str = request.POST.get('recette_realisee', '0')
        recette_realisee = int(float(recette_realisee_str))
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


@login_required
def nouvelle_activite(request):
    """Page de sélection du type d'activité à créer"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    today = date.today()
    
    # Vérifier l'état actuel
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
    
    context = {
        'chauffeur': chauffeur,
        'today': today,
        'prise_aujourdhui': prise_aujourdhui,
        'remise_aujourdhui': remise_aujourdhui,
        'peut_prendre_cles': peut_prendre_cles,
        'peut_remettre_cles': peut_remettre_cles,
    }
    
    return render(request, 'drivers/nouvelle_activite.html', context)


@login_required
def exporter_activite_pdf(request):
    """Export PDF de l'activité de la semaine"""
    try:
        chauffeur = Chauffeur.objects.get(user=request.user)
    except Chauffeur.DoesNotExist:
        messages.error(request, 'Aucun chauffeur associé à votre compte.')
        return redirect('drivers:index')
    
    today = date.today()
    week_start = today - timedelta(days=6)  # 7 jours incluant aujourd'hui
    
    # Récupérer les données de la semaine
    prises_semaine = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('date')
    
    remises_semaine = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=week_start
    ).order_by('date')
    
    pannes_semaine = Panne.objects.filter(
        chauffeur=chauffeur,
        date_creation__gte=week_start
    ).order_by('date_creation')
    
    # Calculer les statistiques
    total_recettes = sum(remise.recette_realisee for remise in remises_semaine)
    moyenne_journaliere = total_recettes / 7 if remises_semaine.count() > 0 else 0
    jours_travailles = remises_semaine.count()
    
    # Créer les données pour chaque jour de la semaine
    jours_semaine = []
    for i in range(7):
        jour_date = week_start + timedelta(days=i)
        jour_nom = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche'][jour_date.weekday()]
        
        prise_jour = prises_semaine.filter(date=jour_date).first()
        remise_jour = remises_semaine.filter(date=jour_date).first()
        
        jours_semaine.append({
            'date': jour_date,
            'nom': jour_nom,
            'prise': prise_jour,
            'remise': remise_jour,
            'recette': remise_jour.recette_realisee if remise_jour else 0,
            'objectif': prise_jour.objectif_recette if prise_jour else 0,
        })
    
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
    
    # Générer le HTML
    html_string = render_to_string('drivers/rapport_semaine_pdf.html', context)
    
    # Créer le PDF
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    # Créer la réponse HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"rapport_semaine_{chauffeur.nom}_{today.strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required
def activite_mensuelle(request):
    """Vue pour l'activité mensuelle avec calendrier"""
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
    }
    
    return render(request, 'drivers/activite_mensuelle.html', context)


def creer_calendrier_mensuel(annee, mois, prises, remises):
    """Créer un calendrier mensuel avec les données d'activité"""
    import calendar
    
    # Créer le calendrier
    cal = calendar.monthcalendar(annee, mois)
    
    # Créer des dictionnaires pour un accès rapide
    prises_dict = {prise.date: prise for prise in prises}
    remises_dict = {remise.date: remise for remise in remises}
    
    calendrier_semaines = []
    
    for semaine in cal:
        semaine_data = []
        for jour in semaine:
            if jour == 0:
                semaine_data.append(None)
            else:
                jour_date = date(annee, mois, jour)
                prise = prises_dict.get(jour_date)
                remise = remises_dict.get(jour_date)
                
                jour_data = {
                    'jour': jour,
                    'date': jour_date,
                    'prise': prise,
                    'remise': remise,
                    'recette': remise.recette_realisee if remise else 0,
                    'objectif': prise.objectif_recette if prise else 0,
                    'actif': prise is not None or remise is not None,
                    'complet': prise is not None and remise is not None,
                }
                
                # Calculer le pourcentage de performance
                if jour_data['objectif'] > 0 and jour_data['recette'] > 0:
                    jour_data['performance'] = int((jour_data['recette'] / jour_data['objectif']) * 100)
                else:
                    jour_data['performance'] = 0
                
                semaine_data.append(jour_data)
        
        calendrier_semaines.append(semaine_data)
    
    return calendrier_semaines
