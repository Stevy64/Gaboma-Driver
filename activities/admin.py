from django.contrib import admin
from .models import Activite, Panne, Recette, PriseCles, RemiseCles


@admin.register(PriseCles)
class PriseClesAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'date', 'heure_prise', 'objectif_recette', 'plein_carburant')
    list_filter = ('date', 'plein_carburant', 'chauffeur')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom', 'probleme_mecanique')
    date_hierarchy = 'date'
    readonly_fields = ('date_creation',)


@admin.register(RemiseCles)
class RemiseClesAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'date', 'heure_remise', 'recette_realisee', 'plein_carburant')
    list_filter = ('date', 'plein_carburant', 'chauffeur')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom', 'probleme_mecanique')
    date_hierarchy = 'date'
    readonly_fields = ('date_creation',)


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'type_activite', 'date_heure', 'recette_jour', 'carburant_info')
    list_filter = ('type_activite', 'date_heure', 'chauffeur')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom', 'notes')
    ordering = ('-date_heure',)
    readonly_fields = ('date_creation',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('chauffeur', 'type_activite', 'date_heure')
        }),
        ('Prise de clés', {
            'fields': ('carburant_litres', 'carburant_pourcentage'),
            'classes': ('collapse',)
        }),
        ('Remise de clés', {
            'fields': ('recette_jour', 'etat_vehicule', 'notes'),
            'classes': ('collapse',)
        }),
        ('Signature', {
            'fields': ('signature',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    
    def carburant_info(self, obj):
        if obj.carburant_litres:
            return f"{obj.carburant_litres}L"
        elif obj.carburant_pourcentage:
            return f"{obj.carburant_pourcentage}%"
        return "-"
    carburant_info.short_description = 'Carburant'


@admin.register(Panne)
class PanneAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'severite', 'statut', 'description_short', 'date_creation')
    list_filter = ('severite', 'statut', 'date_creation', 'chauffeur')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom', 'description')
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('chauffeur', 'activite', 'severite', 'statut')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Réparation', {
            'fields': ('cout_reparation', 'date_reparation'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    def description_short(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'


@admin.register(Recette)
class RecetteAdmin(admin.ModelAdmin):
    list_display = ('chauffeur', 'date', 'montant', 'date_creation')
    list_filter = ('date', 'chauffeur')
    search_fields = ('chauffeur__nom', 'chauffeur__prenom')
    ordering = ('-date',)
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('chauffeur', 'date', 'montant')
        }),
        ('Métadonnées', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )