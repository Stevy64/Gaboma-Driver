from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.http import HttpResponse
from datetime import datetime, date, timedelta
from drivers.models import Chauffeur
from activities.models import Activite, Recette, Panne, PriseCles, RemiseCles, DemandeModification

# Import conditionnel d'openpyxl pour éviter les erreurs si le module n'est pas installé
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


@staff_member_required
def dashboard_admin(request):
    """
    Tableau de bord administrateur avec statistiques en temps réel
    
    Affiche les statistiques générales de l'application :
    - Nombre de chauffeurs actifs
    - Activités du jour (prises et remises)
    - Recettes en FCFA (jour, semaine, mois)
    - Pannes en cours et critiques
    - Top chauffeurs du mois
    - Activités et pannes récentes
    """
    # Statistiques générales
    total_chauffeurs = Chauffeur.objects.filter(actif=True).count()
    
    # Activités du jour (prises et remises)
    prises_aujourdhui = PriseCles.objects.filter(date=date.today()).count()
    remises_aujourdhui = RemiseCles.objects.filter(date=date.today()).count()
    total_activites_aujourdhui = prises_aujourdhui + remises_aujourdhui
    
    # Recettes en FCFA (utilisant les nouveaux modèles)
    recettes_aujourdhui = RemiseCles.objects.filter(
        date=date.today()
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    recettes_semaine = RemiseCles.objects.filter(
        date__gte=date.today() - timedelta(days=7)
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    recettes_mois = RemiseCles.objects.filter(
        date__gte=date.today().replace(day=1)
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    # Pannes (utilisant le modèle Panne)
    pannes_en_cours = Panne.objects.filter(statut='en_cours').count()
    pannes_critiques = Panne.objects.filter(severite='critique').count()
    
    
    # Activités récentes (prises et remises)
    prises_recentes = PriseCles.objects.select_related('chauffeur').order_by('-date', '-heure_prise')[:5]
    remises_recentes = RemiseCles.objects.select_related('chauffeur').order_by('-date', '-heure_remise')[:5]
    
    # Combiner les activités récentes pour l'affichage
    activites_recentes = []
    for prise in prises_recentes:
        activites_recentes.append({
            'chauffeur': prise.chauffeur,
            'type_activite': 'prise',
            'date_heure': f"{prise.date} {prise.heure_prise}",
            'date': prise.date,
            'heure': prise.heure_prise
        })
    for remise in remises_recentes:
        activites_recentes.append({
            'chauffeur': remise.chauffeur,
            'type_activite': 'remise',
            'date_heure': f"{remise.date} {remise.heure_remise}",
            'date': remise.date,
            'heure': remise.heure_remise
        })
    
    # Trier par date décroissante
    activites_recentes.sort(key=lambda x: (x['date'], x['heure']), reverse=True)
    activites_recentes = activites_recentes[:10]
    
    # Demandes de modification en attente
    demandes_en_attente = DemandeModification.objects.filter(statut='en_attente').count()
    
    context = {
        'total_chauffeurs': total_chauffeurs,
        'total_activites_aujourdhui': total_activites_aujourdhui,
        'prises_aujourdhui': prises_aujourdhui,
        'remises_aujourdhui': remises_aujourdhui,
        'recettes_aujourdhui': recettes_aujourdhui,
        'recettes_semaine': recettes_semaine,
        'recettes_mois': recettes_mois,
        'pannes_en_cours': pannes_en_cours,
        'pannes_critiques': pannes_critiques,
        'demandes_en_attente': demandes_en_attente,
        'activites_recentes': activites_recentes,
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
    """
    Statistiques des recettes avec filtres par période et chauffeur
    
    Affiche les recettes en FCFA pour différentes périodes :
    - Par chauffeur avec nombre de jours travaillés
    - Par jour avec évolution temporelle
    - Totaux par période (jour, semaine, mois, année)
    - Graphiques et disques statistiques enrichis
    """
    # Filtres de période et chauffeur
    periode = request.GET.get('periode', 'mois')
    chauffeur_id = request.GET.get('chauffeur', '')
    
    # Définition des périodes
    if periode == 'jour':
        date_debut = date.today()
        date_fin = date.today()
    elif periode == 'semaine':
        # Semaine courante (lundi à dimanche)
        today = date.today()
        date_debut = today - timedelta(days=today.weekday())
        date_fin = date_debut + timedelta(days=6)
    elif periode == 'mois':
        date_debut = date.today().replace(day=1)
        date_fin = date.today()
    elif periode == 'annee':
        date_debut = date.today().replace(month=1, day=1)
        date_fin = date.today()
    else:
        date_debut = date.today().replace(day=1)
        date_fin = date.today()
    
    # Filtre par chauffeur si spécifié
    chauffeur_filter = {}
    if chauffeur_id:
        try:
            chauffeur = Chauffeur.objects.get(id=chauffeur_id)
            chauffeur_filter = {'chauffeur': chauffeur}
        except Chauffeur.DoesNotExist:
            chauffeur = None
    else:
        chauffeur = None
    
    # Recettes par chauffeur (utilisant les nouveaux modèles)
    recettes_chauffeurs = Chauffeur.objects.filter(
        remisecles__date__gte=date_debut,
        remisecles__date__lte=date_fin
    ).annotate(
        total_recettes=Sum('remisecles__recette_realisee'),
        nb_jours=Count('remisecles', distinct=True),
        moyenne_journaliere=Avg('remisecles__recette_realisee')
    ).filter(total_recettes__gt=0).order_by('-total_recettes')
    
    # Recettes par jour (utilisant les nouveaux modèles)
    recettes_par_jour = RemiseCles.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin,
        **chauffeur_filter
    ).values('date').annotate(
        total=Sum('recette_realisee'),
        nb_chauffeurs=Count('chauffeur', distinct=True)
    ).order_by('date')
    
    # Calcul des totaux
    recette_totale = RemiseCles.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin,
        **chauffeur_filter
    ).aggregate(Sum('recette_realisee'))['recette_realisee__sum'] or 0
    
    # Statistiques supplémentaires
    nombre_chauffeurs_actifs = recettes_chauffeurs.count()
    moyenne_par_chauffeur = recette_totale / nombre_chauffeurs_actifs if nombre_chauffeurs_actifs > 0 else 0
    
    # Données pour les graphiques
    # 1. Données pour le graphique en barres (recettes par jour)
    chart_data_daily = []
    for recette_jour in recettes_par_jour:
        chart_data_daily.append({
            'date': recette_jour['date'].strftime('%d/%m'),
            'recette': float(recette_jour['total']),
            'nb_chauffeurs': recette_jour['nb_chauffeurs']
        })
    
    # 2. Données pour le graphique en secteurs (répartition par chauffeur)
    chart_data_chauffeurs = []
    for chauffeur_data in recettes_chauffeurs:
        chart_data_chauffeurs.append({
            'nom': chauffeur_data.nom_complet,
            'recette': float(chauffeur_data.total_recettes),
            'nb_jours': chauffeur_data.nb_jours,
            'moyenne': float(chauffeur_data.moyenne_journaliere or 0)
        })
    
    # 3. Statistiques pour les disques de performance
    # Calcul de la performance moyenne
    performances_chauffeurs = []
    for chauffeur_data in recettes_chauffeurs:
        # Récupérer les objectifs pour ce chauffeur sur la période
        objectifs_chauffeur = PriseCles.objects.filter(
            chauffeur=chauffeur_data,
            date__gte=date_debut,
            date__lte=date_fin
        ).aggregate(Sum('objectif_recette'))['objectif_recette__sum'] or 0
        
        performance = (chauffeur_data.total_recettes / objectifs_chauffeur * 100) if objectifs_chauffeur > 0 else 0
        performances_chauffeurs.append({
            'chauffeur': chauffeur_data.nom_complet,
            'performance': performance,
            'recette': chauffeur_data.total_recettes,
            'objectif': objectifs_chauffeur
        })
    
    # Performance moyenne globale
    performance_moyenne = sum(p['performance'] for p in performances_chauffeurs) / len(performances_chauffeurs) if performances_chauffeurs else 0
    
    # 4. Données pour l'évolution temporelle (si période > jour)
    evolution_data = []
    if periode in ['semaine', 'mois', 'annee']:
        # Calculer les totaux par sous-période
        if periode == 'semaine':
            # Par jour de la semaine
            for i in range(7):
                jour_date = date_debut + timedelta(days=i)
                if jour_date <= date_fin:
                    recette_jour = RemiseCles.objects.filter(
                        date=jour_date,
                        **chauffeur_filter
                    ).aggregate(Sum('recette_realisee'))['recette_realisee__sum'] or 0
                    evolution_data.append({
                        'periode': jour_date.strftime('%A'),
                        'recette': float(recette_jour)
                    })
        elif periode == 'mois':
            # Par semaine du mois
            semaine_actuelle = 1
            recette_semaine = 0
            for recette_jour in recettes_par_jour:
                semaine_jour = recette_jour['date'].isocalendar()[1]
                if semaine_jour != semaine_actuelle:
                    evolution_data.append({
                        'periode': f'Semaine {semaine_actuelle}',
                        'recette': float(recette_semaine)
                    })
                    semaine_actuelle = semaine_jour
                    recette_semaine = recette_jour['total']
                else:
                    recette_semaine += recette_jour['total']
            # Ajouter la dernière semaine
            if recette_semaine > 0:
                evolution_data.append({
                    'periode': f'Semaine {semaine_actuelle}',
                    'recette': float(recette_semaine)
                })
        elif periode == 'annee':
            # Par mois de l'année
            for mois in range(1, 13):
                recette_mois = RemiseCles.objects.filter(
                    date__year=date.today().year,
                    date__month=mois,
                    **chauffeur_filter
                ).aggregate(Sum('recette_realisee'))['recette_realisee__sum'] or 0
                evolution_data.append({
                    'periode': f'{mois:02d}',
                    'recette': float(recette_mois)
                })
    
    # Liste de tous les chauffeurs pour le filtre
    tous_chauffeurs = Chauffeur.objects.all().order_by('nom', 'prenom')
    
    context = {
        'periode': periode,
        'chauffeur_selectionne': chauffeur,
        'chauffeur_id': chauffeur_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'recettes_chauffeurs': recettes_chauffeurs,
        'recettes_par_jour': recettes_par_jour,
        'recette_totale': recette_totale,
        'nombre_chauffeurs_actifs': nombre_chauffeurs_actifs,
        'moyenne_par_chauffeur': moyenne_par_chauffeur,
        'recette_jour': recette_totale if periode == 'jour' else 0,
        'recette_semaine': recette_totale if periode == 'semaine' else 0,
        'recette_mois': recette_totale if periode == 'mois' else 0,
        'recette_annee': recette_totale if periode == 'annee' else 0,
        # Données pour les graphiques
        'chart_data_daily': chart_data_daily,
        'chart_data_chauffeurs': chart_data_chauffeurs,
        'performances_chauffeurs': performances_chauffeurs,
        'performance_moyenne': performance_moyenne,
        'evolution_data': evolution_data,
        'tous_chauffeurs': tous_chauffeurs,
    }
    
    return render(request, 'admin_dashboard/statistiques_recettes.html', context)


@staff_member_required
def calendrier_activites(request):
    """
    Calendrier des activités pour l'administrateur
    
    Utilise la même logique que le calendrier chauffeur mais pour tous les chauffeurs.
    """
    from datetime import timedelta
    import calendar
    
    # Paramètres de navigation
    today = date.today()
    annee = int(request.GET.get('annee', today.year))
    mois = int(request.GET.get('mois', today.month))
    chauffeur_id = request.GET.get('chauffeur')
    
    # Calculer les dates de début et fin du mois
    mois_debut = date(annee, mois, 1)
    if mois == 12:
        mois_fin = date(annee + 1, 1, 1) - timedelta(days=1)
    else:
        mois_fin = date(annee, mois + 1, 1) - timedelta(days=1)
    
    # Récupération des chauffeurs pour le filtre
    chauffeurs = Chauffeur.objects.all().order_by('nom', 'prenom')
    
    # Récupération des données du mois
    prises_query = PriseCles.objects.filter(
        date__gte=mois_debut,
        date__lte=mois_fin
    ).select_related('chauffeur').order_by('date')
    
    remises_query = RemiseCles.objects.filter(
        date__gte=mois_debut,
        date__lte=mois_fin
    ).select_related('chauffeur').order_by('date')
    
    # Filtrage par chauffeur si spécifié
    if chauffeur_id:
        prises_query = prises_query.filter(chauffeur_id=chauffeur_id)
        remises_query = remises_query.filter(chauffeur_id=chauffeur_id)
    
    prises_mois = list(prises_query)
    remises_mois = list(remises_query)
    
    # Créer le calendrier du mois (même logique que chauffeur)
    calendrier = creer_calendrier_admin_mensuel(annee, mois, prises_mois, remises_mois)
    
    # Calculer les statistiques du mois
    total_mois = sum(remise.recette_realisee for remise in remises_mois)
    jours_travailles = len(remises_mois)
    moyenne_journaliere = total_mois / jours_travailles if jours_travailles > 0 else 0
    
    # Statistiques par mois de l'année
    stats_par_mois = []
    for m in range(1, 13):
        mois_debut_m = date(annee, m, 1)
        if m == 12:
            mois_fin_m = date(annee + 1, 1, 1) - timedelta(days=1)
        else:
            mois_fin_m = date(annee, m + 1, 1) - timedelta(days=1)
        
        remises_m = RemiseCles.objects.filter(
            date__gte=mois_debut_m, 
            date__lte=mois_fin_m
        )
        if chauffeur_id:
            remises_m = remises_m.filter(chauffeur_id=chauffeur_id)
            
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
        'stats_par_mois': stats_par_mois,
        'chauffeurs': chauffeurs,
        'chauffeur_selectionne': chauffeur_id,
        'today': today,
    }
    
    return render(request, 'admin_dashboard/calendrier_activites.html', context)


def creer_calendrier_admin_mensuel(annee, mois, prises, remises):
    """
    Créer un calendrier mensuel avec les données d'activité pour l'admin
    
    Version adaptée de la fonction chauffeur pour gérer plusieurs chauffeurs.
    """
    import calendar
    
    # Création du calendrier du mois avec le module calendar
    cal = calendar.monthcalendar(annee, mois)
    
    # Création de dictionnaires pour un accès rapide aux données
    prises_dict = {}
    remises_dict = {}
    
    # Grouper par date pour gérer plusieurs chauffeurs
    for prise in prises:
        if prise.date not in prises_dict:
            prises_dict[prise.date] = []
        prises_dict[prise.date].append(prise)
    
    for remise in remises:
        if remise.date not in remises_dict:
            remises_dict[remise.date] = []
        remises_dict[remise.date].append(remise)
    
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
                prises_jour = prises_dict.get(jour_date, [])
                remises_jour = remises_dict.get(jour_date, [])
                
                # Calcul des totaux pour ce jour
                total_recette = sum(remise.recette_realisee for remise in remises_jour)
                total_objectif = sum(prise.objectif_recette for prise in prises_jour)
                
                # Construction des données du jour
                jour_data = {
                    'jour': jour,
                    'date': jour_date,
                    'prises': prises_jour,
                    'remises': remises_jour,
                    'recette': total_recette,
                    'objectif': total_objectif,
                    'actif': len(prises_jour) > 0 or len(remises_jour) > 0,
                    'complet': len(prises_jour) > 0 and len(remises_jour) > 0,
                }
                
                # Calcul du pourcentage de performance
                if jour_data['objectif'] > 0 and jour_data['recette'] > 0:
                    jour_data['performance'] = int((jour_data['recette'] / jour_data['objectif']) * 100)
                else:
                    jour_data['performance'] = 0
                
                semaine_data.append(jour_data)
        
        calendrier_semaines.append(semaine_data)
    
    return calendrier_semaines


@staff_member_required
def gestion_pannes(request):
    """Gestion des pannes"""
    pannes = Panne.objects.select_related('chauffeur').order_by('-date_creation')
    
    # Filtres
    statut = request.GET.get('statut')
    severite = request.GET.get('severite')
    
    if statut:
        pannes = pannes.filter(resolue=(statut == 'resolue'))
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
    """
    Classements et gamification des chauffeurs
    
    Affiche les classements par recettes :
    - Top chauffeurs du jour
    - Top chauffeurs de la semaine
    - Top chauffeurs du mois
    - Statistiques de présence
    """
    
    # Top chauffeurs du jour (utilisant les nouveaux modèles)
    top_jour = Chauffeur.objects.filter(
        remisecles__date=date.today()
    ).annotate(
        recette_jour=Sum('remisecles__recette_realisee')
    ).filter(recette_jour__gt=0).order_by('-recette_jour')[:3]
    
    # Top chauffeurs de la semaine (lundi au dimanche)
    semaine_debut = date.today() - timedelta(days=date.today().weekday())
    top_semaine = Chauffeur.objects.filter(
        remisecles__date__gte=semaine_debut
    ).annotate(
        recette_semaine=Sum('remisecles__recette_realisee')
    ).filter(recette_semaine__gt=0).order_by('-recette_semaine')[:3]
    
    # Top chauffeurs du mois (1er au dernier jour du mois)
    mois_debut = date.today().replace(day=1)
    top_mois = Chauffeur.objects.filter(
        remisecles__date__gte=mois_debut
    ).annotate(
        recette_mois=Sum('remisecles__recette_realisee')
    ).filter(recette_mois__gt=0).order_by('-recette_mois')[:3]
    
    # Statistiques de présence (utilisant les nouveaux modèles)
    presence_semaine = Chauffeur.objects.annotate(
        jours_travailles=Count('prisecles', filter=Q(
            prisecles__date__gte=semaine_debut
        ), distinct=True)
    ).filter(jours_travailles__gt=0).order_by('-jours_travailles')
    
    # Statistiques globales
    total_recettes_jour = RemiseCles.objects.filter(
        date=date.today()
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    total_recettes_semaine = RemiseCles.objects.filter(
        date__gte=semaine_debut
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    total_recettes_mois = RemiseCles.objects.filter(
        date__gte=mois_debut
    ).aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    context = {
        'top_jour': top_jour,
        'top_semaine': top_semaine,
        'top_mois': top_mois,
        'presence_semaine': presence_semaine,
        'total_recettes_jour': total_recettes_jour,
        'total_recettes_semaine': total_recettes_semaine,
        'total_recettes_mois': total_recettes_mois,
    }
    
    return render(request, 'admin_dashboard/classements.html', context)


# =============================================================================
# GESTION DES ACTIVITÉS - Nouvelles fonctionnalités administrateur
# =============================================================================

@staff_member_required
def gestion_activites(request):
    """
    Vue pour la gestion des activités par chauffeur
    
    Permet aux administrateurs de voir toutes les activités (prises et remises de clés)
    par chauffeur avec possibilité de filtrer et de consulter les détails.
    """
    # Récupération des paramètres de filtrage
    chauffeur_id = request.GET.get('chauffeur')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    type_activite = request.GET.get('type_activite')
    
    # Filtrage des chauffeurs
    chauffeurs = Chauffeur.objects.filter(actif=True).order_by('nom', 'prenom')
    
    # Récupération des activités avec filtres
    prises = PriseCles.objects.select_related('chauffeur').all()
    remises = RemiseCles.objects.select_related('chauffeur').all()
    
    # Application des filtres
    if chauffeur_id:
        prises = prises.filter(chauffeur_id=chauffeur_id)
        remises = remises.filter(chauffeur_id=chauffeur_id)
    
    if date_debut:
        try:
            date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
            prises = prises.filter(date__gte=date_debut_obj)
            remises = remises.filter(date__gte=date_debut_obj)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
            prises = prises.filter(date__lte=date_fin_obj)
            remises = remises.filter(date__lte=date_fin_obj)
        except ValueError:
            pass
    
    # Tri par date décroissante
    prises = prises.order_by('-date', '-heure_prise')
    remises = remises.order_by('-date', '-heure_remise')
    
    # Filtrage par type d'activité (pour l'affichage)
    if type_activite == 'prise':
        remises = remises.none()  # Afficher seulement les prises
    elif type_activite == 'remise':
        prises = prises.none()  # Afficher seulement les remises
    
    # Pagination pour les prises
    prises_paginator = Paginator(prises, 15)  # 15 éléments par page
    prises_page = request.GET.get('prises_page')
    prises_obj = prises_paginator.get_page(prises_page)
    
    # Pagination pour les remises
    remises_paginator = Paginator(remises, 15)  # 15 éléments par page
    remises_page = request.GET.get('remises_page')
    remises_obj = remises_paginator.get_page(remises_page)
    
    # Statistiques
    total_prises = prises.count()
    total_remises = remises.count()
    
    # Calcul des recettes totales pour la période
    recettes_totales = remises.aggregate(total=Sum('recette_realisee'))['total'] or 0
    
    context = {
        'chauffeurs': chauffeurs,
        'prises': prises_obj,
        'remises': remises_obj,
        'prises_paginator': prises_paginator,
        'remises_paginator': remises_paginator,
        'total_prises': total_prises,
        'total_remises': total_remises,
        'recettes_totales': recettes_totales,
        'filtres': {
            'chauffeur_id': chauffeur_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'type_activite': type_activite,
        },
        'filtres_applied': {
            'chauffeur': chauffeur_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'type_activite': type_activite,
        }
    }
    
    return render(request, 'admin_dashboard/gestion_activites.html', context)


@staff_member_required
def activites_chauffeur(request, chauffeur_id):
    """
    Vue détaillée des activités d'un chauffeur spécifique
    
    Affiche toutes les activités d'un chauffeur avec possibilité de voir
    les détails complets et les performances.
    """
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # Récupération des activités du chauffeur
    prises = PriseCles.objects.filter(chauffeur=chauffeur).order_by('-date', '-heure_prise')
    remises = RemiseCles.objects.filter(chauffeur=chauffeur).order_by('-date', '-heure_remise')
    
    # Pagination pour les prises
    prises_paginator = Paginator(prises, 15)
    prises_page = request.GET.get('prises_page')
    prises_obj = prises_paginator.get_page(prises_page)
    
    # Pagination pour les remises
    remises_paginator = Paginator(remises, 15)
    remises_page = request.GET.get('remises_page')
    remises_obj = remises_paginator.get_page(remises_page)
    
    # Statistiques du chauffeur
    total_prises = prises.count()
    total_remises = remises.count()
    
    # Calcul des performances
    performances = []
    for remise in remises:
        try:
            prise = PriseCles.objects.get(chauffeur=chauffeur, date=remise.date)
            pourcentage = (remise.recette_realisee / prise.objectif_recette) * 100
            performances.append({
                'date': remise.date,
                'objectif': prise.objectif_recette,
                'realise': remise.recette_realisee,
                'pourcentage': pourcentage,
                'statut': 'success' if pourcentage >= 100 else 'warning' if pourcentage >= 90 else 'danger'
            })
        except PriseCles.DoesNotExist:
            performances.append({
                'date': remise.date,
                'objectif': 0,
                'realise': remise.recette_realisee,
                'pourcentage': 0,
                'statut': 'info'
            })
    
    # Statistiques globales
    recettes_totales = remises.aggregate(total=Sum('recette_realisee'))['total'] or 0
    objectifs_totaux = prises.aggregate(total=Sum('objectif_recette'))['total'] or 0
    performance_moyenne = (recettes_totales / objectifs_totaux * 100) if objectifs_totaux > 0 else 0
    
    context = {
        'chauffeur': chauffeur,
        'prises': prises_obj,
        'remises': remises_obj,
        'prises_paginator': prises_paginator,
        'remises_paginator': remises_paginator,
        'performances': performances,
        'total_prises': total_prises,
        'total_remises': total_remises,
        'recettes_totales': recettes_totales,
        'objectifs_totaux': objectifs_totaux,
        'performance_moyenne': performance_moyenne,
    }
    
    return render(request, 'admin_dashboard/activites_chauffeur.html', context)


@staff_member_required
def exporter_activite_chauffeur_pdf(request, chauffeur_id):
    """
    Vue pour exporter les activités d'un chauffeur en PDF
    
    Génère un rapport PDF mensuel complet des activités d'un chauffeur avec
    les jours travaillés, recettes réalisées, performances et totaux par semaine.
    """
    chauffeur = get_object_or_404(Chauffeur, id=chauffeur_id)
    
    # Récupération des paramètres de filtrage (par défaut: mois en cours)
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Si aucune date n'est spécifiée, utiliser le mois en cours
    if not date_debut or not date_fin:
        today = timezone.now().date()
        # Premier jour du mois
        date_debut = today.replace(day=1)
        # Dernier jour du mois
        if today.month == 12:
            date_fin = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            date_fin = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    
    # Conversion des dates
    if isinstance(date_debut, str):
        date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
    if isinstance(date_fin, str):
        date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
    
    # Récupération des activités du chauffeur pour le mois
    prises = PriseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=date_debut,
        date__lte=date_fin
    ).order_by('date', 'heure_prise')
    
    remises = RemiseCles.objects.filter(
        chauffeur=chauffeur,
        date__gte=date_debut,
        date__lte=date_fin
    ).order_by('date', 'heure_remise')
    
    # Calcul des statistiques générales
    total_prises = prises.count()
    total_remises = remises.count()
    recettes_totales = remises.aggregate(total=Sum('recette_realisee'))['total'] or 0
    objectifs_totaux = prises.aggregate(total=Sum('objectif_recette'))['total'] or 0
    performance_moyenne = (recettes_totales / objectifs_totaux * 100) if objectifs_totaux > 0 else 0
    
    # Calcul des performances par jour avec détails
    performances_journalieres = []
    jours_travailles = set()
    
    for remise in remises:
        jours_travailles.add(remise.date)
        try:
            prise = PriseCles.objects.get(chauffeur=chauffeur, date=remise.date)
            pourcentage = (remise.recette_realisee / prise.objectif_recette) * 100
            performances_journalieres.append({
                'date': remise.date,
                'jour_semaine': remise.date.strftime('%A'),
                'objectif': prise.objectif_recette,
                'realise': remise.recette_realisee,
                'pourcentage': pourcentage,
                'statut': 'success' if pourcentage >= 100 else 'warning' if pourcentage >= 90 else 'danger',
                'heure_prise': prise.heure_prise,
                'heure_remise': remise.heure_remise,
                'plein_carburant': remise.plein_carburant,
                'probleme_mecanique': remise.probleme_mecanique
            })
        except PriseCles.DoesNotExist:
            performances_journalieres.append({
                'date': remise.date,
                'jour_semaine': remise.date.strftime('%A'),
                'objectif': 0,
                'realise': remise.recette_realisee,
                'pourcentage': 0,
                'statut': 'info',
                'heure_prise': None,
                'heure_remise': remise.heure_remise,
                'plein_carburant': remise.plein_carburant,
                'probleme_mecanique': remise.probleme_mecanique
            })
    
    # Calcul des totaux par semaine
    totaux_semaines = []
    semaine_courante = None
    recette_semaine = 0
    objectif_semaine = 0
    jours_semaine = 0
    
    for perf in performances_journalieres:
        # Calcul du numéro de semaine
        semaine_num = perf['date'].isocalendar()[1]
        
        if semaine_courante is None:
            semaine_courante = semaine_num
        
        if semaine_num != semaine_courante:
            # Finaliser la semaine précédente
            totaux_semaines.append({
                'semaine': semaine_courante,
                'recette': recette_semaine,
                'objectif': objectif_semaine,
                'jours': jours_semaine,
                'performance': (recette_semaine / objectif_semaine * 100) if objectif_semaine > 0 else 0
            })
            # Commencer une nouvelle semaine
            semaine_courante = semaine_num
            recette_semaine = perf['realise']
            objectif_semaine = perf['objectif']
            jours_semaine = 1
        else:
            recette_semaine += perf['realise']
            objectif_semaine += perf['objectif']
            jours_semaine += 1
    
    # Ajouter la dernière semaine
    if semaine_courante is not None:
        totaux_semaines.append({
            'semaine': semaine_courante,
            'recette': recette_semaine,
            'objectif': objectif_semaine,
            'jours': jours_semaine,
            'performance': (recette_semaine / objectif_semaine * 100) if objectif_semaine > 0 else 0
        })
    
    # Préparation du contexte pour le PDF
    context = {
        'chauffeur': chauffeur,
        'prises': prises,
        'remises': remises,
        'performances_journalieres': performances_journalieres,
        'totaux_semaines': totaux_semaines,
        'total_prises': total_prises,
        'total_remises': total_remises,
        'recettes_totales': recettes_totales,
        'objectifs_totaux': objectifs_totaux,
        'performance_moyenne': performance_moyenne,
        'jours_travailles': len(jours_travailles),
        'date_debut': date_debut,
        'date_fin': date_fin,
        'date_generation': timezone.now(),
        'mois_nom': date_debut.strftime('%B %Y'),
    }
    
    # Génération du PDF
    try:
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        import weasyprint
        
        html_string = render_to_string('admin_dashboard/rapport_mensuel_chauffeur_pdf.html', context)
        html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        mois_str = date_debut.strftime('%Y-%m')
        response['Content-Disposition'] = f'attachment; filename="rapport_mensuel_{chauffeur.nom}_{chauffeur.prenom}_{mois_str}.pdf"'
        return response
        
    except ImportError:
        messages.error(request, 'Le module weasyprint n\'est pas installé. Impossible de générer le PDF.')
        return redirect('admin_dashboard:activites_chauffeur', chauffeur_id=chauffeur_id)
    except Exception as e:
        messages.error(request, f'Erreur lors de la génération du PDF: {str(e)}')
        return redirect('admin_dashboard:activites_chauffeur', chauffeur_id=chauffeur_id)


@staff_member_required
def gestion_demandes_modification(request):
    """
    Vue pour la gestion des demandes de modification d'activité
    
    Permet aux administrateurs de voir toutes les demandes de modification
    et de les approuver ou rejeter avec commentaires.
    """
    # Récupération des paramètres de filtrage
    statut = request.GET.get('statut', 'en_attente')
    chauffeur_id = request.GET.get('chauffeur')
    
    # Récupération des demandes avec filtres
    demandes = DemandeModification.objects.select_related('chauffeur', 'admin_traite').all()
    
    if statut:
        demandes = demandes.filter(statut=statut)
    
    if chauffeur_id:
        demandes = demandes.filter(chauffeur_id=chauffeur_id)
    
    # Tri par date de création décroissante
    demandes = demandes.order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(demandes, 15)  # 15 éléments par page
    page_number = request.GET.get('page')
    demandes_obj = paginator.get_page(page_number)
    
    # Liste des chauffeurs pour le filtre
    chauffeurs = Chauffeur.objects.filter(actif=True).order_by('nom', 'prenom')
    
    # Statistiques
    total_demandes = demandes.count()
    demandes_en_attente = DemandeModification.objects.filter(statut='en_attente').count()
    demandes_approuvees = DemandeModification.objects.filter(statut='approuvee').count()
    demandes_rejetees = DemandeModification.objects.filter(statut='rejetee').count()
    
    context = {
        'demandes': demandes_obj,
        'paginator': paginator,
        'chauffeurs': chauffeurs,
        'total_demandes': total_demandes,
        'demandes_en_attente': demandes_en_attente,
        'demandes_approuvees': demandes_approuvees,
        'demandes_rejetees': demandes_rejetees,
        'filtres': {
            'statut': statut,
            'chauffeur_id': chauffeur_id,
        }
    }
    
    return render(request, 'admin_dashboard/gestion_demandes_modification.html', context)


@staff_member_required
def traiter_demande_modification(request, demande_id):
    """
    Vue pour traiter une demande de modification spécifique
    
    Permet à l'administrateur d'approuver ou rejeter une demande
    avec commentaires et d'appliquer les modifications si approuvée.
    """
    demande = get_object_or_404(DemandeModification, id=demande_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        commentaire = request.POST.get('commentaire', '')
        
        if action in ['approuver', 'rejeter']:
            # Traitement de la demande
            demande.traiter(
                admin=request.user,
                approuvee=(action == 'approuver'),
                commentaire=commentaire
            )
            
            # Si approuvée, appliquer les modifications
            if action == 'approuver':
                try:
                    if demande.type_activite == 'prise':
                        activite = PriseCles.objects.get(
                            chauffeur=demande.chauffeur, 
                            date=demande.date_activite
                        )
                    else:
                        activite = RemiseCles.objects.get(
                            chauffeur=demande.chauffeur, 
                            date=demande.date_activite
                        )
                    
                    # Application des nouvelles données
                    nouvelles_donnees = demande.nouvelles_donnees
                    for champ, valeur in nouvelles_donnees.items():
                        if hasattr(activite, champ):
                            setattr(activite, champ, valeur)
                    
                    activite.save()
                    
                    messages.success(request, f'Demande approuvée et modifications appliquées avec succès.')
                except Exception as e:
                    messages.error(request, f'Erreur lors de l\'application des modifications: {str(e)}')
            else:
                messages.success(request, 'Demande rejetée avec succès.')
            
            return redirect('admin_dashboard:gestion_demandes_modification')
    
    # Récupération de l'activité concernée pour affichage
    activite_actuelle = None
    try:
        if demande.type_activite == 'prise':
            activite_actuelle = PriseCles.objects.get(
                chauffeur=demande.chauffeur, 
                date=demande.date_activite
            )
        else:
            activite_actuelle = RemiseCles.objects.get(
                chauffeur=demande.chauffeur, 
                date=demande.date_activite
            )
    except (PriseCles.DoesNotExist, RemiseCles.DoesNotExist):
        pass
    
    context = {
        'demande': demande,
        'activite_actuelle': activite_actuelle,
    }
    
    return render(request, 'admin_dashboard/traiter_demande_modification.html', context)


@staff_member_required
def exporter_excel(request):
    """
    Export des données de recettes et performances en fichier Excel
    
    Génère un fichier Excel contenant toutes les données selon les filtres :
    - Période : jour, semaine, mois, année
    - Chauffeur : spécifique ou tous
    """
    # Vérifier si openpyxl est disponible
    if not OPENPYXL_AVAILABLE:
        messages.error(request, "Le module openpyxl n'est pas installé. Veuillez installer openpyxl pour utiliser cette fonctionnalité.")
        return redirect('admin_dashboard:statistiques_recettes')
    
    try:
        # Récupération des paramètres de filtre
        periode = request.GET.get('periode', 'mois')
        chauffeur_id = request.GET.get('chauffeur')
        
        # Calcul des dates selon la période
        aujourd_hui = timezone.now().date()
        
        if periode == 'jour':
            date_debut = aujourd_hui
            date_fin = aujourd_hui
        elif periode == 'semaine':
            # Lundi de cette semaine
            date_debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
            date_fin = date_debut + timedelta(days=6)
        elif periode == 'mois':
            date_debut = aujourd_hui.replace(day=1)
            if aujourd_hui.month == 12:
                date_fin = aujourd_hui.replace(year=aujourd_hui.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                date_fin = aujourd_hui.replace(month=aujourd_hui.month + 1, day=1) - timedelta(days=1)
        else:  # annee
            date_debut = aujourd_hui.replace(month=1, day=1)
            date_fin = aujourd_hui.replace(month=12, day=31)
        
        # Filtrage des données
        chauffeur_filter = Q()
        if chauffeur_id:
            chauffeur_filter = Q(chauffeur_id=chauffeur_id)
        
        # Récupération des données
        prises = PriseCles.objects.filter(
            chauffeur_filter,
            date__range=[date_debut, date_fin]
        ).order_by('date', 'chauffeur__nom')
        
        remises = RemiseCles.objects.filter(
            chauffeur_filter,
            date__range=[date_debut, date_fin]
        ).order_by('date', 'chauffeur__nom')
        
        # Création du fichier Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        # Titre limité à 31 caractères pour Excel
        ws.title = f"Recettes_{periode}_{date_debut.strftime('%m%d')}"
        
        # Styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # En-têtes
        headers = [
            'Date', 'Chauffeur', 'Heure Début', 'Heure Fin', 
            'Objectif (FCFA)', 'Recette Réalisée (FCFA)', 'Performance (%)',
            'Carburant Plein', 'Problème Mécanique (Début)', 'Problème Mécanique (Fin)'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
            cell.border = border
        
        # Données
        row = 2
        for prise in prises:
            # Trouver la remise correspondante
            remise = remises.filter(
                chauffeur=prise.chauffeur,
                date=prise.date
            ).first()
            
            # Calcul de la performance
            performance = 0
            if prise.objectif_recette and prise.objectif_recette > 0:
                recette_reelle = remise.recette_realisee if remise else 0
                performance = (recette_reelle / prise.objectif_recette) * 100
            
            # Données de la ligne
            data = [
                prise.date.strftime('%d/%m/%Y'),
                prise.chauffeur.nom_complet,
                prise.heure_prise.strftime('%H:%M') if prise.heure_prise else '',
                remise.heure_remise.strftime('%H:%M') if remise and remise.heure_remise else '',
                prise.objectif_recette or 0,
                remise.recette_realisee if remise else 0,
                round(performance, 1),
                'Oui' if prise.plein_carburant else 'Non',
                prise.probleme_mecanique or 'Aucun',
                remise.probleme_mecanique if remise else ''
            ]
            
            # Écriture des données
            for col, value in enumerate(data, 1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.border = border
                if col in [5, 6]:  # Colonnes monétaires
                    cell.number_format = '#,##0'
                elif col == 7:  # Performance
                    cell.number_format = '0.0'
            
            row += 1
        
        # Résumé
        ws.cell(row=row + 1, column=1, value="RÉSUMÉ").font = Font(bold=True)
        ws.cell(row=row + 2, column=1, value="Période:").font = Font(bold=True)
        ws.cell(row=row + 2, column=2, value=f"{date_debut.strftime('%d/%m/%Y')} - {date_fin.strftime('%d/%m/%Y')}")
        
        ws.cell(row=row + 3, column=1, value="Total Recettes:").font = Font(bold=True)
        total_recettes = sum(remise.recette_realisee for remise in remises if remise.recette_realisee)
        ws.cell(row=row + 3, column=2, value=total_recettes).number_format = '#,##0'
        
        ws.cell(row=row + 4, column=1, value="Total Objectifs:").font = Font(bold=True)
        total_objectifs = sum(prise.objectif_recette for prise in prises if prise.objectif_recette)
        ws.cell(row=row + 4, column=2, value=total_objectifs).number_format = '#,##0'
        
        ws.cell(row=row + 5, column=1, value="Performance Moyenne:").font = Font(bold=True)
        performance_moyenne = (total_recettes / total_objectifs * 100) if total_objectifs > 0 else 0
        ws.cell(row=row + 5, column=2, value=round(performance_moyenne, 1)).number_format = '0.0'
        
        # Ajustement des colonnes
        for col in range(1, len(headers) + 1):
            column_letter = get_column_letter(col)
            ws.column_dimensions[column_letter].width = 15
        
        # Nom du fichier
        chauffeur_nom = ""
        if chauffeur_id:
            try:
                chauffeur = Chauffeur.objects.get(id=chauffeur_id)
                chauffeur_nom = f"_{chauffeur.nom}_{chauffeur.prenom}"
            except Chauffeur.DoesNotExist:
                pass
        
        filename = f"recettes_{periode}{chauffeur_nom}_{date_debut.strftime('%Y%m%d')}_{date_fin.strftime('%Y%m%d')}.xlsx"
        
        # Réponse HTTP
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        return response
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du fichier Excel : {str(e)}")
        return redirect('admin_dashboard:statistiques_recettes')