# =============================================================================
# MODÈLES DE L'APPLICATION ACTIVITIES - Gestion des activités de taxi
# =============================================================================

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from drivers.models import Chauffeur


class PriseCles(models.Model):
    """
    Modèle pour représenter la prise de clés du matin par un chauffeur
    
    Ce modèle enregistre toutes les informations relatives à la prise de clés
    le matin : objectif de recette, état du véhicule, problèmes mécaniques,
    et signature électronique du chauffeur.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque prise est associée à un chauffeur
    - unique_together avec date : un chauffeur ne peut prendre les clés qu'une fois par jour
    
    Utilisation :
    - Enregistrement quotidien de la prise de clés
    - Suivi des objectifs de recette
    - Gestion des problèmes mécaniques
    - Traçabilité avec signature électronique
    """
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec le chauffeur
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur qui prend les clés"
    )
    
    # Informations temporelles
    date = models.DateField(
        verbose_name="Date",
        help_text="Date de prise des clés"
    )
    heure_prise = models.TimeField(
        verbose_name="Heure de prise",
        help_text="Heure à laquelle les clés ont été prises"
    )
    
    # Objectif de la journée
    objectif_recette = models.IntegerField(
        validators=[MinValueValidator(0)],  # Validation : valeur positive
        verbose_name="Objectif de recette (FCFA)",
        help_text="Objectif de recette fixé pour la journée en FCFA"
    )
    
    # État du véhicule au moment de la prise
    plein_carburant = models.BooleanField(
        default=False,
        verbose_name="Plein de carburant",
        help_text="Indique si le véhicule a le plein de carburant"
    )
    
    # Problèmes mécaniques signalés
    probleme_mecanique = models.CharField(
        max_length=200,
        default="Aucun",
        verbose_name="Problème mécanique",
        help_text="Description des problèmes mécaniques éventuels"
    )
    
    # Signature électronique pour traçabilité
    signature = models.TextField(
        verbose_name="Signature électronique",
        help_text="Signature électronique du chauffeur"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création de l'enregistrement"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Prise de clés"                    # Nom singulier dans l'admin
        verbose_name_plural = "Prises de clés"            # Nom pluriel dans l'admin
        ordering = ['-date', '-heure_prise']              # Tri par date puis heure (plus récent en premier)
        unique_together = ['chauffeur', 'date']           # Contrainte : une seule prise par jour par chauffeur
        db_table = 'activities_prise_cles'                # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de la prise de clés
        
        Returns:
            str: "Nom Complet - Prise Date - Objectif FCFA"
        """
        return f"{self.chauffeur.nom_complet} - Prise {self.date} - {self.objectif_recette} FCFA"
    
    def get_duree_travail(self):
        """
        Calcule la durée de travail si une remise de clés existe
        
        Returns:
            timedelta or None: Durée de travail ou None si pas de remise
        """
        try:
            remise = RemiseCles.objects.get(chauffeur=self.chauffeur, date=self.date)
            from datetime import datetime, time
            debut = datetime.combine(self.date, self.heure_prise)
            fin = datetime.combine(remise.date, remise.heure_remise)
            return fin - debut
        except RemiseCles.DoesNotExist:
            return None
    
    def est_jour_complet(self):
        """
        Vérifie si la journée est complète (prise + remise)
        
        Returns:
            bool: True si la journée est complète
        """
        return RemiseCles.objects.filter(
            chauffeur=self.chauffeur, 
            date=self.date
        ).exists()


class RemiseCles(models.Model):
    """
    Modèle pour représenter la remise de clés du soir par un chauffeur
    
    Ce modèle enregistre toutes les informations relatives à la remise de clés
    le soir : recette réalisée, état du véhicule, problèmes mécaniques,
    et signature électronique du chauffeur.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque remise est associée à un chauffeur
    - unique_together avec date : un chauffeur ne peut remettre les clés qu'une fois par jour
    - Relation implicite avec PriseCles via chauffeur + date
    
    Utilisation :
    - Enregistrement quotidien de la remise de clés
    - Calcul de la performance par rapport à l'objectif
    - Suivi des recettes réalisées
    - Gestion des problèmes mécaniques
    - Traçabilité avec signature électronique
    """
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec le chauffeur
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur qui remet les clés"
    )
    
    # Informations temporelles
    date = models.DateField(
        verbose_name="Date",
        help_text="Date de remise des clés"
    )
    heure_remise = models.TimeField(
        verbose_name="Heure de remise",
        help_text="Heure à laquelle les clés ont été remises"
    )
    
    # Recette réalisée pendant la journée
    recette_realisee = models.IntegerField(
        validators=[MinValueValidator(0)],  # Validation : valeur positive
        verbose_name="Recette réalisée (FCFA)",
        help_text="Montant de la recette réalisée pendant la journée en FCFA"
    )
    
    # État du véhicule au moment de la remise
    plein_carburant = models.BooleanField(
        default=False,
        verbose_name="Plein de carburant",
        help_text="Indique si le véhicule a le plein de carburant"
    )
    
    # Problèmes mécaniques signalés
    probleme_mecanique = models.CharField(
        max_length=200,
        default="Aucun",
        verbose_name="Problème mécanique",
        help_text="Description des problèmes mécaniques éventuels"
    )
    
    # Signature électronique pour traçabilité
    signature = models.TextField(
        verbose_name="Signature électronique",
        help_text="Signature électronique du chauffeur"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création de l'enregistrement"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Remise de clés"                  # Nom singulier dans l'admin
        verbose_name_plural = "Remises de clés"          # Nom pluriel dans l'admin
        ordering = ['-date', '-heure_remise']            # Tri par date puis heure (plus récent en premier)
        unique_together = ['chauffeur', 'date']          # Contrainte : une seule remise par jour par chauffeur
        db_table = 'activities_remise_cles'              # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de la remise de clés
        
        Returns:
            str: "Nom Complet - Remise Date - Recette FCFA"
        """
        return f"{self.chauffeur.nom_complet} - Remise {self.date} - {self.recette_realisee} FCFA"
    
    def get_objectif_atteint(self):
        """
        Calcule si l'objectif de recette a été atteint
        
        Cette méthode compare la recette réalisée avec l'objectif fixé
        lors de la prise de clés et retourne un statut avec message.
        
        Returns:
            tuple: (type_alerte, message) où type_alerte est 'success', 'warning', 'danger' ou 'info'
        """
        try:
            # Récupération de la prise de clés correspondante
            prise = PriseCles.objects.get(chauffeur=self.chauffeur, date=self.date)
            
            # Calcul du pourcentage de réalisation
            pourcentage = (self.recette_realisee / prise.objectif_recette) * 100
            
            # Détermination du statut selon le pourcentage
            if pourcentage >= 100:
                return 'success', f"🎉 Bravo ! Objectif atteint avec succès ({pourcentage:.1f}%)"
            elif pourcentage >= 90:
                return 'warning', f"⚠️ Presque atteint ! Encore un petit effort ({pourcentage:.1f}%)"
            else:
                return 'danger', f"❌ Objectif non atteint. Courage, demain sera meilleur ! ({pourcentage:.1f}%)"
        except PriseCles.DoesNotExist:
            return 'info', "ℹ️ Aucun objectif défini pour cette journée"
    
    def get_performance_pourcentage(self):
        """
        Calcule le pourcentage de performance par rapport à l'objectif
        
        Returns:
            float: Pourcentage de performance (0-100+)
        """
        try:
            prise = PriseCles.objects.get(chauffeur=self.chauffeur, date=self.date)
            return (self.recette_realisee / prise.objectif_recette) * 100
        except PriseCles.DoesNotExist:
            return 0.0


class Activite(models.Model):
    """
    Modèle legacy pour représenter une activité de prise/remise de clés
    
    ATTENTION : Ce modèle est marqué comme legacy et ne devrait plus être utilisé
    dans le développement de nouvelles fonctionnalités. Il est conservé pour
    la compatibilité avec les données existantes.
    
    Utilisez plutôt les modèles PriseCles et RemiseCles qui offrent
    une séparation claire et une meilleure structure.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque activité est associée à un chauffeur
    
    Utilisation :
    - Lecture des données historiques
    - Migration vers les nouveaux modèles
    - Pas de nouvelles créations recommandées
    """
    
    # =============================================================================
    # CHOIX POUR LES CHAMPS - Définition des options disponibles
    # =============================================================================
    
    TYPE_ACTIVITE_CHOICES = [
        ('prise', 'Prise de clés'),
        ('remise', 'Remise de clés'),
    ]
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec le chauffeur
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur associé à cette activité"
    )
    
    # Type d'activité (prise ou remise)
    type_activite = models.CharField(
        max_length=10, 
        choices=TYPE_ACTIVITE_CHOICES,
        verbose_name="Type d'activité",
        help_text="Type d'activité : prise ou remise de clés"
    )
    
    # Date et heure de l'activité
    date_heure = models.DateTimeField(
        verbose_name="Date et heure",
        help_text="Date et heure de l'activité"
    )
    
    # Informations de prise de clés (legacy)
    carburant_litres = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Carburant (litres)",
        help_text="Quantité de carburant en litres (legacy)"
    )
    carburant_pourcentage = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Carburant (%)",
        help_text="Pourcentage de carburant (legacy)"
    )
    
    # Informations de remise de clés (legacy)
    recette_jour = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Recette du jour (€)",
        help_text="Recette réalisée en euros (legacy)"
    )
    etat_vehicule = models.TextField(
        null=True, 
        blank=True,
        verbose_name="État du véhicule",
        help_text="Description de l'état du véhicule (legacy)"
    )
    notes = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Notes",
        help_text="Notes additionnelles (legacy)"
    )
    
    # Signature électronique
    signature = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Signature",
        help_text="Signature électronique du chauffeur"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création de l'enregistrement"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Activité (Legacy)"                # Nom singulier dans l'admin
        verbose_name_plural = "Activités (Legacy)"        # Nom pluriel dans l'admin
        ordering = ['-date_heure']                        # Tri par date/heure (plus récent en premier)
        db_table = 'activities_activite_legacy'           # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de l'activité legacy
        
        Returns:
            str: "Nom Complet - Type Activité - Date Heure"
        """
        return f"{self.chauffeur.nom_complet} - {self.get_type_activite_display()} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"


class Panne(models.Model):
    """
    Modèle pour représenter les pannes et problèmes mécaniques des véhicules
    
    Ce modèle permet de suivre les pannes signalées par les chauffeurs,
    leur niveau de sévérité, leur statut de résolution et les coûts associés.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque panne est associée à un chauffeur
    - ForeignKey vers Activite (optionnel) : panne liée à une activité spécifique
    
    Utilisation :
    - Signalement des problèmes mécaniques
    - Suivi des réparations
    - Calcul des coûts de maintenance
    - Historique des pannes par véhicule
    """
    
    # =============================================================================
    # CHOIX POUR LES CHAMPS - Définition des options disponibles
    # =============================================================================
    
    SEVERITE_CHOICES = [
        ('mineure', 'Mineure'),      # Problème mineur, pas d'impact sur le service
        ('moderee', 'Modérée'),      # Problème modéré, impact limité
        ('majeure', 'Majeure'),      # Problème majeur, impact significatif
        ('critique', 'Critique'),    # Problème critique, véhicule hors service
    ]
    
    STATUT_CHOICES = [
        ('signalee', 'Signalée'),                    # Panne signalée, en attente
        ('en_cours', 'En cours de réparation'),      # Réparation en cours
        ('reparée', 'Réparée'),                      # Panne résolue
        ('annulee', 'Annulée'),                      # Signalement annulé (faux positif)
    ]
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relations
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur qui a signalé la panne"
    )
    activite = models.ForeignKey(
        Activite, 
        on_delete=models.CASCADE,  # Suppression en cascade si l'activité est supprimée
        null=True,                 # Optionnel : panne non liée à une activité
        blank=True,                # Permet de laisser vide dans les formulaires
        verbose_name="Activité liée",
        help_text="Activité associée à la panne (optionnel)"
    )
    
    # Description de la panne
    description = models.TextField(
        verbose_name="Description du problème",
        help_text="Description détaillée du problème mécanique"
    )
    severite = models.CharField(
        max_length=10, 
        choices=SEVERITE_CHOICES,
        default='mineure',
        verbose_name="Sévérité",
        help_text="Niveau de sévérité de la panne"
    )
    statut = models.CharField(
        max_length=10, 
        choices=STATUT_CHOICES,
        default='signalee',
        verbose_name="Statut",
        help_text="Statut actuel de la panne"
    )
    
    # Coûts et réparations
    cout_reparation = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Coût de réparation (€)",
        help_text="Coût de la réparation en euros"
    )
    date_reparation = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de réparation",
        help_text="Date et heure de la réparation"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de signalement de la panne"
    )
    date_modification = models.DateTimeField(
        auto_now=True, 
        verbose_name="Dernière modification",
        help_text="Date et heure de la dernière modification"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Panne"                        # Nom singulier dans l'admin
        verbose_name_plural = "Pannes"                # Nom pluriel dans l'admin
        ordering = ['-date_creation']                 # Tri par date de création (plus récent en premier)
        db_table = 'activities_panne'                 # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de la panne
        
        Returns:
            str: "Nom Complet - Sévérité - Description (tronquée)"
        """
        return f"{self.chauffeur.nom_complet} - {self.get_severite_display()} - {self.description[:50]}..."
    
    def est_resolue(self):
        """
        Vérifie si la panne est résolue
        
        Returns:
            bool: True si la panne est résolue
        """
        return self.statut == 'reparée'
    
    def est_critique(self):
        """
        Vérifie si la panne est critique
        
        Returns:
            bool: True si la panne est critique
        """
        return self.severite == 'critique'


class Recette(models.Model):
    """
    Modèle pour représenter les recettes journalières des chauffeurs
    
    Ce modèle legacy stocke les recettes journalières des chauffeurs.
    Il est conservé pour la compatibilité avec les données existantes
    mais n'est plus utilisé dans les nouvelles fonctionnalités.
    
    Utilisez plutôt le modèle RemiseCles qui contient la recette_realisee
    et offre une meilleure intégration avec le système de prise/remise de clés.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque recette est associée à un chauffeur
    - unique_together avec date : une recette par chauffeur par jour
    
    Utilisation :
    - Lecture des données historiques
    - Migration vers le nouveau système
    - Pas de nouvelles créations recommandées
    """
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec le chauffeur
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur associé à cette recette"
    )
    
    # Informations temporelles
    date = models.DateField(
        verbose_name="Date",
        help_text="Date de la recette"
    )
    
    # Montant de la recette
    montant = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],  # Validation : valeur positive
        verbose_name="Montant (€)",
        help_text="Montant de la recette en euros (legacy)"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création de l'enregistrement"
    )
    date_modification = models.DateTimeField(
        auto_now=True, 
        verbose_name="Dernière modification",
        help_text="Date et heure de la dernière modification"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Recette"                        # Nom singulier dans l'admin
        verbose_name_plural = "Recettes"                # Nom pluriel dans l'admin
        ordering = ['-date']                            # Tri par date (plus récent en premier)
        unique_together = ['chauffeur', 'date']         # Contrainte : une recette par chauffeur par jour
        db_table = 'activities_recette_legacy'          # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de la recette
        
        Returns:
            str: "Nom Complet - Date - Montant€"
        """
        return f"{self.chauffeur.nom_complet} - {self.date} - {self.montant}€"


class DemandeModification(models.Model):
    """
    Modèle pour gérer les demandes de modification d'activité par les chauffeurs
    
    Ce modèle permet aux chauffeurs de demander la modification d'une activité
    déjà enregistrée (prise ou remise de clés). Le processus nécessite l'approbation
    d'un administrateur avant que les modifications ne soient appliquées.
    
    Relations :
    - ForeignKey vers Chauffeur : chaque demande est associée à un chauffeur
    - ForeignKey vers User (optionnel) : admin qui a traité la demande
    
    Utilisation :
    - Demande de modification par les chauffeurs
    - Workflow d'approbation par les administrateurs
    - Traçabilité des modifications
    - Historique des changements
    """
    
    # =============================================================================
    # CHOIX POUR LES CHAMPS - Définition des options disponibles
    # =============================================================================
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),      # Demande en attente de traitement
        ('approuvee', 'Approuvée'),        # Demande approuvée par l'admin
        ('rejetee', 'Rejetée'),            # Demande rejetée par l'admin
    ]
    
    TYPE_ACTIVITE_CHOICES = [
        ('prise', 'Prise de clés'),        # Modification d'une prise de clés
        ('remise', 'Remise de clés'),      # Modification d'une remise de clés
    ]
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec le chauffeur demandeur
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE,  # Suppression en cascade si le chauffeur est supprimé
        verbose_name="Chauffeur",
        help_text="Chauffeur qui fait la demande de modification"
    )
    
    # Type d'activité à modifier
    type_activite = models.CharField(
        max_length=10,
        choices=TYPE_ACTIVITE_CHOICES,
        verbose_name="Type d'activité",
        help_text="Type d'activité à modifier : prise ou remise de clés"
    )
    
    # Date de l'activité à modifier
    date_activite = models.DateField(
        verbose_name="Date de l'activité",
        help_text="Date de l'activité à modifier"
    )
    
    # Données originales (JSON)
    donnees_originales = models.JSONField(
        verbose_name="Données originales",
        help_text="Données originales de l'activité avant modification"
    )
    
    # Nouvelles données proposées (JSON)
    nouvelles_donnees = models.JSONField(
        verbose_name="Nouvelles données",
        help_text="Nouvelles données proposées pour l'activité"
    )
    
    # Raison de la modification
    raison = models.TextField(
        verbose_name="Raison de la modification",
        help_text="Justification de la demande de modification"
    )
    
    # Statut de la demande
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut",
        help_text="Statut actuel de la demande"
    )
    
    # Admin qui a traité la demande
    admin_traite = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,  # Conserve la demande même si l'admin est supprimé
        null=True,
        blank=True,
        verbose_name="Admin qui a traité",
        help_text="Administrateur qui a traité cette demande"
    )
    
    # Commentaire de l'admin
    commentaire_admin = models.TextField(
        blank=True,
        verbose_name="Commentaire de l'admin",
        help_text="Commentaire de l'administrateur sur la demande"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création de la demande"
    )
    date_traitement = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement",
        help_text="Date et heure de traitement de la demande par l'admin"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Demande de modification"         # Nom singulier dans l'admin
        verbose_name_plural = "Demandes de modification" # Nom pluriel dans l'admin
        ordering = ['-date_creation']                    # Tri par date de création (plus récent en premier)
        db_table = 'activities_demande_modification'     # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de la demande de modification
        
        Returns:
            str: "Nom Complet - Type Activité - Date - Statut"
        """
        return f"{self.chauffeur.nom_complet} - {self.get_type_activite_display()} - {self.date_activite} - {self.get_statut_display()}"
    
    def est_en_attente(self):
        """
        Vérifie si la demande est en attente
        
        Returns:
            bool: True si la demande est en attente
        """
        return self.statut == 'en_attente'
    
    def est_approuvee(self):
        """
        Vérifie si la demande est approuvée
        
        Returns:
            bool: True si la demande est approuvée
        """
        return self.statut == 'approuvee'
    
    def est_rejetee(self):
        """
        Vérifie si la demande est rejetée
        
        Returns:
            bool: True si la demande est rejetée
        """
        return self.statut == 'rejetee'
    
    def traiter(self, admin, approuvee=True, commentaire=""):
        """
        Traite une demande de modification
        
        Args:
            admin (User): Administrateur qui traite la demande
            approuvee (bool): True si approuvée, False si rejetée
            commentaire (str): Commentaire de l'administrateur
        """
        from django.utils import timezone
        
        self.admin_traite = admin
        self.commentaire_admin = commentaire
        self.statut = 'approuvee' if approuvee else 'rejetee'
        self.date_traitement = timezone.now()
        self.save()