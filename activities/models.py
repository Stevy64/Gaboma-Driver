from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from drivers.models import Chauffeur


class Activite(models.Model):
    """Modèle pour représenter une activité de prise/remise de clés"""
    
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
        verbose_name = "Activité"
        verbose_name_plural = "Activités"
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