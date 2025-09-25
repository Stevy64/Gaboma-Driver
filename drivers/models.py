# =============================================================================
# MODÈLES DE L'APPLICATION DRIVERS - Gestion des chauffeurs
# =============================================================================

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Chauffeur(models.Model):
    """
    Modèle pour représenter un chauffeur de taxi dans l'application Gaboma Drive
    
    Ce modèle stocke toutes les informations relatives à un chauffeur :
    - Informations personnelles (nom, prénom, téléphone, email)
    - Liaison avec le système d'authentification Django
    - Statut d'activation et dates de suivi
    
    Relations :
    - OneToOne avec User : chaque chauffeur a un compte utilisateur unique
    - ForeignKey depuis PriseCles, RemiseCles, Panne, Recette, DemandeModification
    
    Utilisation :
    - Création via l'interface admin ou l'API
    - Authentification via le système Django
    - Suivi des activités quotidiennes
    """
    
    # =============================================================================
    # CHAMPS DU MODÈLE - Définition des attributs de la base de données
    # =============================================================================
    
    # Informations personnelles du chauffeur
    nom = models.CharField(
        max_length=100, 
        verbose_name="Nom",
        help_text="Nom de famille du chauffeur"
    )
    prenom = models.CharField(
        max_length=100, 
        verbose_name="Prénom",
        help_text="Prénom du chauffeur"
    )
    telephone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Format de téléphone invalide"
        )],
        verbose_name="Téléphone",
        help_text="Numéro de téléphone (format international accepté)"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Adresse email de contact"
    )
    
    # Liaison avec le système d'authentification Django
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # Suppression en cascade si l'utilisateur est supprimé
        null=True,                 # Permet de créer un chauffeur sans compte utilisateur
        blank=True,                # Permet de laisser vide dans les formulaires
        verbose_name="Compte utilisateur",
        help_text="Compte utilisateur Django associé"
    )
    
    # Statut et suivi temporel
    actif = models.BooleanField(
        default=True, 
        verbose_name="Actif",
        help_text="Indique si le chauffeur est actif dans le système"
    )
    date_creation = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Date de création",
        help_text="Date et heure de création du profil chauffeur"
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
        ordering = ['nom', 'prenom']                  # Tri par défaut : nom puis prénom
        db_table = 'drivers_chauffeur'                # Nom de la table en base
    
    # =============================================================================
    # MÉTHODES DU MODÈLE - Fonctionnalités personnalisées
    # =============================================================================
    
    def __str__(self):
        """
        Représentation textuelle du chauffeur
        
        Returns:
            str: "Prénom Nom" du chauffeur
        """
        return f"{self.prenom} {self.nom}"
    
    @property
    def nom_complet(self):
        """
        Propriété pour obtenir le nom complet du chauffeur
        
        Cette propriété est utilisée dans les templates et l'API
        pour afficher le nom complet de manière cohérente.
        
        Returns:
            str: "Prénom Nom" du chauffeur
        """
        return f"{self.prenom} {self.nom}"
    
    def est_actif(self):
        """
        Vérifie si le chauffeur est actif
        
        Returns:
            bool: True si le chauffeur est actif, False sinon
        """
        return self.actif and self.user is not None and self.user.is_active
    
    def peut_travailler(self):
        """
        Vérifie si le chauffeur peut travailler (actif + compte valide)
        
        Returns:
            bool: True si le chauffeur peut travailler
        """
        return (self.est_actif() and 
                self.user is not None and 
                self.user.is_authenticated)