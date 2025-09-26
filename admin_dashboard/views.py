from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, date, timedelta
from drivers.models import Chauffeur
from activities.models import Activite, Recette, Panne, PriseCles, RemiseCles, DemandeModification


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
    
    # Pannes récentes
    pannes_recentes = Panne.objects.select_related('chauffeur').order_by('-date_creation')[:5]
    
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
    """
    Statistiques des recettes avec filtres par période
    
    Affiche les recettes en FCFA pour différentes périodes :
    - Par chauffeur avec nombre de jours travaillés
    - Par jour avec évolution temporelle
    - Totaux par période (jour, semaine, mois, année)
    """
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
    
    # Recettes par chauffeur (utilisant les nouveaux modèles)
    recettes_chauffeurs = Chauffeur.objects.filter(
        remisecles__date__gte=date_debut,
        remisecles__date__lte=date_fin
    ).annotate(
        total_recettes=Sum('remisecles__recette_realisee'),
        nb_jours=Count('remisecles', distinct=True)
    ).filter(total_recettes__gt=0).order_by('-total_recettes')
    
    # Recettes par jour (utilisant les nouveaux modèles)
    recettes_par_jour = RemiseCles.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin
    ).values('date').annotate(
        total=Sum('recette_realisee')
    ).order_by('date')
    
    # Calcul des totaux
    recette_totale = RemiseCles.objects.filter(
        date__gte=date_debut,
        date__lte=date_fin
    ).aggregate(Sum('recette_realisee'))['recette_realisee__sum'] or 0
    
    # Statistiques supplémentaires
    nombre_chauffeurs_actifs = recettes_chauffeurs.count()
    moyenne_par_chauffeur = recette_totale / nombre_chauffeurs_actifs if nombre_chauffeurs_actifs > 0 else 0
    
    context = {
        'periode': periode,
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
    prises_paginator = Paginator(prises, 10)  # 10 éléments par page
    prises_page = request.GET.get('prises_page')
    prises_obj = prises_paginator.get_page(prises_page)
    
    # Pagination pour les remises
    remises_paginator = Paginator(remises, 10)  # 10 éléments par page
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
    prises_paginator = Paginator(prises, 10)
    prises_page = request.GET.get('prises_page')
    prises_obj = prises_paginator.get_page(prises_page)
    
    # Pagination pour les remises
    remises_paginator = Paginator(remises, 10)
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