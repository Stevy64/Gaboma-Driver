# =============================================================================
# MODÈLES DE L'APPLICATION DRIVERS - Gestion des chauffeurs
# =============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone


class Chauffeur(models.Model):
    """
    Modèle pour représenter un chauffeur de taxi
    
    Ce modèle stocke toutes les informations relatives à un chauffeur :
    - Informations personnelles (nom, prénom, téléphone, email)
    - Informations de compte (utilisateur Django associé)
    - Statut d'activité et métadonnées de suivi
    
    Relations :
    - OneToOne vers User : chaque chauffeur est associé à un utilisateur Django
    - ManyToMany vers User (superviseurs) : assignation des superviseurs
    
    Utilisation :
    - Authentification des chauffeurs
    - Gestion des profils
    - Suivi des activités
    - Assignation aux superviseurs
    """
    
    # =============================================================================
    # VALIDATEURS - Contrôles de validation des données
    # =============================================================================
    
    # Validateur pour le numéro de téléphone gabonais
    phone_validator = RegexValidator(
        regex=r'^(\+241|0)[0-9]{8}$',
        message='Le numéro de téléphone doit être au format gabonais (+241XXXXXXXX ou 0XXXXXXXX)'
    )
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relation avec l'utilisateur Django
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # Suppression en cascade si l'utilisateur est supprimé
        verbose_name="Utilisateur",
        help_text="Utilisateur Django associé à ce chauffeur"
    )
    
    # Informations personnelles
    nom = models.CharField(
        max_length=50,
        verbose_name="Nom",
        help_text="Nom de famille du chauffeur"
    )
    prenom = models.CharField(
        max_length=50,
        verbose_name="Prénom",
        help_text="Prénom du chauffeur"
    )
    telephone = models.CharField(
        max_length=15,
        validators=[phone_validator],
        verbose_name="Téléphone",
        help_text="Numéro de téléphone au format gabonais"
    )
    email = models.EmailField(
        blank=True,
        verbose_name="Email",
        help_text="Adresse email du chauffeur (optionnel)"
    )
    
    # Statut et activité
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le chauffeur est actif"
    )
    
    # Métadonnées de suivi
    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date et heure de création du profil"
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
        verbose_name = "Chauffeur"                    # Nom singulier dans l'admin
        verbose_name_plural = "Chauffeurs"            # Nom pluriel dans l'admin
        ordering = ['nom', 'prenom']                  # Tri par nom puis prénom
        db_table = 'drivers_chauffeur'                # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle du chauffeur
        
        Returns:
            str: "Prénom Nom"
        """
        return f"{self.prenom} {self.nom}"
    
    @property
    def nom_complet(self):
        """
        Propriété pour obtenir le nom complet
        
        Returns:
            str: "Prénom Nom"
        """
        return f"{self.prenom} {self.nom}"
    
    def get_derniere_activite(self):
        """
        Récupère la dernière activité du chauffeur
        
        Returns:
            PriseCles or RemiseCles or None: Dernière activité ou None
        """
        from activities.models import PriseCles, RemiseCles
        
        # Récupérer la dernière prise et la dernière remise
        derniere_prise = PriseCles.objects.filter(chauffeur=self).order_by('-date', '-heure_prise').first()
        derniere_remise = RemiseCles.objects.filter(chauffeur=self).order_by('-date', '-heure_remise').first()
        
        # Retourner la plus récente
        if derniere_prise and derniere_remise:
            if derniere_prise.date > derniere_remise.date:
                return derniere_prise
            elif derniere_remise.date > derniere_prise.date:
                return derniere_remise
            else:
                # Même date, comparer les heures
                if derniere_prise.heure_prise > derniere_remise.heure_remise:
                    return derniere_prise
                else:
                    return derniere_remise
        elif derniere_prise:
            return derniere_prise
        elif derniere_remise:
            return derniere_remise
        else:
            return None
    
    def get_statut_activite(self):
        """
        Détermine le statut d'activité du chauffeur
        
        Returns:
            str: Statut ('actif', 'inactif', 'en_cours')
        """
        if not self.actif:
            return 'inactif'
        
        derniere_activite = self.get_derniere_activite()
        if not derniere_activite:
            return 'inactif'
        
        # Vérifier si c'est une prise de clés (début de journée)
        if hasattr(derniere_activite, 'heure_prise'):
            # C'est une prise de clés, vérifier s'il y a une remise correspondante
            from activities.models import RemiseCles
            remise = RemiseCles.objects.filter(
                chauffeur=self,
                date=derniere_activite.date
            ).first()
            
            if not remise:
                return 'en_cours'  # Prise de clés sans remise = en cours
            else:
                return 'actif'  # Journée complète
        else:
            # C'est une remise de clés, journée terminée
            return 'actif'


class AssignationSuperviseur(models.Model):
    """
    Modèle pour gérer l'assignation des chauffeurs aux superviseurs
    
    Ce modèle permet de créer une relation many-to-many entre les chauffeurs
    et les superviseurs, avec des métadonnées de suivi.
    
    Relations :
    - ForeignKey vers Chauffeur : chauffeur assigné
    - ForeignKey vers User : superviseur assigné
    
    Utilisation :
    - Assignation des chauffeurs aux superviseurs
    - Filtrage des données par superviseur
    - Historique des assignations
    """
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Relations
    chauffeur = models.ForeignKey(
        Chauffeur,
        on_delete=models.CASCADE,
        verbose_name="Chauffeur",
        help_text="Chauffeur assigné"
    )
    superviseur = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Superviseurs'},
        verbose_name="Superviseur",
        help_text="Superviseur assigné"
    )
    
    # Métadonnées de suivi
    date_assignation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'assignation",
        help_text="Date et heure de l'assignation"
    )
    assigne_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignations_effectuees',
        verbose_name="Assigné par",
        help_text="Utilisateur qui a effectué l'assignation"
    )
    actif = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'assignation est active"
    )
    
    # =============================================================================
    # MÉTADONNÉES DU MODÈLE - Configuration Django
    # =============================================================================
    
    class Meta:
        verbose_name = "Assignation Superviseur"
        verbose_name_plural = "Assignations Superviseurs"
        ordering = ['-date_assignation']
        unique_together = ['chauffeur', 'superviseur']
        db_table = 'drivers_assignation_superviseur'
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle de l'assignation
        
        Returns:
            str: "Chauffeur - Superviseur"
        """
        return f"{self.chauffeur.nom_complet} - {self.superviseur.get_full_name() or self.superviseur.username}"
    
    @classmethod
    def get_chauffeurs_assignes(cls, superviseur):
        """
        Récupère tous les chauffeurs assignés à un superviseur
        
        Args:
            superviseur (User): Superviseur
            
        Returns:
            QuerySet: Chauffeurs assignés
        """
        return Chauffeur.objects.filter(
            assignationsuperviseur__superviseur=superviseur,
            assignationsuperviseur__actif=True
        ).distinct()
    
    @classmethod
    def get_superviseurs_assignes(cls, chauffeur):
        """
        Récupère tous les superviseurs assignés à un chauffeur
        
        Args:
            chauffeur (Chauffeur): Chauffeur
            
        Returns:
            QuerySet: Superviseurs assignés
        """
        return User.objects.filter(
            assignationsuperviseur__chauffeur=chauffeur,
            assignationsuperviseur__actif=True
        ).distinct()