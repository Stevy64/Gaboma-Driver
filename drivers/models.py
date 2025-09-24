from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Chauffeur(models.Model):
    """Modèle pour représenter un chauffeur de taxi"""
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Format de téléphone invalide"
        )],
        verbose_name="Téléphone"
    )
    email = models.EmailField(verbose_name="Email")
    
    # Informations de compte
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Compte utilisateur"
    )
    
    # Statut
    actif = models.BooleanField(default=True, verbose_name="Actif")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"