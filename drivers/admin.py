from django.contrib import admin
from .models import Chauffeur


@admin.register(Chauffeur)
class ChauffeurAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'telephone', 'email', 'actif', 'date_creation')
    list_filter = ('actif', 'date_creation')
    search_fields = ('nom', 'prenom', 'telephone', 'email')
    ordering = ('nom', 'prenom')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'telephone', 'email')
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'description': 'Lier à un compte utilisateur Django pour la connexion'
        }),
        ('Statut', {
            'fields': ('actif',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def nom_complet(self, obj):
        return obj.nom_complet
    nom_complet.short_description = 'Nom complet'