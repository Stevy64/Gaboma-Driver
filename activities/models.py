from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from drivers.models import Chauffeur


class PriseCles(models.Model):
    """Modèle pour représenter la prise de clés du matin"""
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    date = models.DateField(verbose_name="Date")
    heure_prise = models.TimeField(verbose_name="Heure de prise")
    
    # Objectif de la journée
    objectif_recette = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Objectif de recette (FCFA)"
    )
    
    # État du véhicule
    plein_carburant = models.BooleanField(
        default=False,
        verbose_name="Plein de carburant"
    )
    
    # Problèmes mécaniques
    probleme_mecanique = models.CharField(
        max_length=200,
        default="Aucun",
        verbose_name="Problème mécanique"
    )
    
    # Signature électronique
    signature = models.TextField(
        verbose_name="Signature électronique"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Prise de clés"
        verbose_name_plural = "Prises de clés"
        ordering = ['-date', '-heure_prise']
        unique_together = ['chauffeur', 'date']  # Une seule prise par jour par chauffeur
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - Prise {self.date} - {self.objectif_recette} FCFA"


class RemiseCles(models.Model):
    """Modèle pour représenter la remise de clés du soir"""
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    date = models.DateField(verbose_name="Date")
    heure_remise = models.TimeField(verbose_name="Heure de remise")
    
    # Recette réalisée
    recette_realisee = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Recette réalisée (FCFA)"
    )
    
    # État du véhicule
    plein_carburant = models.BooleanField(
        default=False,
        verbose_name="Plein de carburant"
    )
    
    # Problèmes mécaniques
    probleme_mecanique = models.CharField(
        max_length=200,
        default="Aucun",
        verbose_name="Problème mécanique"
    )
    
    # Signature électronique
    signature = models.TextField(
        verbose_name="Signature électronique"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Remise de clés"
        verbose_name_plural = "Remises de clés"
        ordering = ['-date', '-heure_remise']
        unique_together = ['chauffeur', 'date']  # Une seule remise par jour par chauffeur
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - Remise {self.date} - {self.recette_realisee} FCFA"
    
    def get_objectif_atteint(self):
        """Calcule si l'objectif a été atteint"""
        try:
            prise = PriseCles.objects.get(chauffeur=self.chauffeur, date=self.date)
            pourcentage = (self.recette_realisee / prise.objectif_recette) * 100
            
            if pourcentage >= 100:
                return 'success', f"🎉 Bravo ! Objectif atteint avec succès ({pourcentage:.1f}%)"
            elif pourcentage >= 90:
                return 'warning', f"⚠️ Presque atteint ! Encore un petit effort ({pourcentage:.1f}%)"
            else:
                return 'danger', f"❌ Objectif non atteint. Courage, demain sera meilleur ! ({pourcentage:.1f}%)"
        except PriseCles.DoesNotExist:
            return 'info', "ℹ️ Aucun objectif défini pour cette journée"


class Activite(models.Model):
    """Modèle pour représenter une activité de prise/remise de clés (legacy)"""
    
    TYPE_ACTIVITE_CHOICES = [
        ('prise', 'Prise de clés'),
        ('remise', 'Remise de clés'),
    ]
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    type_activite = models.CharField(
        max_length=10, 
        choices=TYPE_ACTIVITE_CHOICES,
        verbose_name="Type d'activité"
    )
    date_heure = models.DateTimeField(verbose_name="Date et heure")
    
    # Informations de prise de clés
    carburant_litres = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Carburant (litres)"
    )
    carburant_pourcentage = models.IntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Carburant (%)"
    )
    
    # Informations de remise de clés
    recette_jour = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Recette du jour (€)"
    )
    etat_vehicule = models.TextField(
        null=True, 
        blank=True,
        verbose_name="État du véhicule"
    )
    notes = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Notes"
    )
    
    # Signature électronique (texte simple pour commencer)
    signature = models.TextField(
        null=True, 
        blank=True,
        verbose_name="Signature"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Activité (Legacy)"
        verbose_name_plural = "Activités (Legacy)"
        ordering = ['-date_heure']
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - {self.get_type_activite_display()} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"


class Panne(models.Model):
    """Modèle pour représenter les pannes et problèmes mécaniques"""
    
    SEVERITE_CHOICES = [
        ('mineure', 'Mineure'),
        ('moderee', 'Modérée'),
        ('majeure', 'Majeure'),
        ('critique', 'Critique'),
    ]
    
    STATUT_CHOICES = [
        ('signalee', 'Signalée'),
        ('en_cours', 'En cours de réparation'),
        ('reparée', 'Réparée'),
        ('annulee', 'Annulée'),
    ]
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    activite = models.ForeignKey(
        Activite, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Activité liée"
    )
    
    # Description de la panne
    description = models.TextField(verbose_name="Description du problème")
    severite = models.CharField(
        max_length=10, 
        choices=SEVERITE_CHOICES,
        default='mineure',
        verbose_name="Sévérité"
    )
    statut = models.CharField(
        max_length=10, 
        choices=STATUT_CHOICES,
        default='signalee',
        verbose_name="Statut"
    )
    
    # Coûts et réparations
    cout_reparation = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Coût de réparation (€)"
    )
    date_reparation = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Date de réparation"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Panne"
        verbose_name_plural = "Pannes"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - {self.get_severite_display()} - {self.description[:50]}..."


class Recette(models.Model):
    """Modèle pour représenter les recettes journalières"""
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    date = models.DateField(verbose_name="Date")
    montant = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Montant (€)"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ['-date']
        unique_together = ['chauffeur', 'date']  # Une recette par chauffeur par jour
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - {self.date} - {self.montant}€"


class DemandeModification(models.Model):
    """Modèle pour les demandes de modification d'activité"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
    ]
    
    TYPE_ACTIVITE_CHOICES = [
        ('prise', 'Prise de clés'),
        ('remise', 'Remise de clés'),
    ]
    
    chauffeur = models.ForeignKey(
        Chauffeur, 
        on_delete=models.CASCADE, 
        verbose_name="Chauffeur"
    )
    
    type_activite = models.CharField(
        max_length=10,
        choices=TYPE_ACTIVITE_CHOICES,
        verbose_name="Type d'activité"
    )
    
    date_activite = models.DateField(verbose_name="Date de l'activité")
    
    # Données originales
    donnees_originales = models.JSONField(verbose_name="Données originales")
    
    # Nouvelles données proposées
    nouvelles_donnees = models.JSONField(verbose_name="Nouvelles données")
    
    # Raison de la modification
    raison = models.TextField(verbose_name="Raison de la modification")
    
    # Statut de la demande
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    
    # Admin qui a traité la demande
    admin_traite = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Admin qui a traité"
    )
    
    # Commentaire de l'admin
    commentaire_admin = models.TextField(
        blank=True,
        verbose_name="Commentaire de l'admin"
    )
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_traitement = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de traitement"
    )
    
    class Meta:
        verbose_name = "Demande de modification"
        verbose_name_plural = "Demandes de modification"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.chauffeur.nom_complet} - {self.get_type_activite_display()} - {self.date_activite} - {self.get_statut_display()}"