# =============================================================================
# ADMIN PERSONNALISÉ - Gestion des utilisateurs avec suppression sécurisée
# =============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from drivers.models import Chauffeur, AssignationSuperviseur
from activities.models import DemandeModification


class CustomUserAdmin(UserAdmin):
    """
    Administration personnalisée des utilisateurs avec gestion sécurisée de la suppression
    
    Cette classe étend UserAdmin pour ajouter :
    - Actions personnalisées de suppression
    - Vérification des dépendances avant suppression
    - Suppression en cascade sécurisée
    - Informations sur les relations
    """
    
    # Ajouter des colonnes personnalisées dans la liste
    list_display = UserAdmin.list_display + ('get_chauffeur_info', 'get_superviseur_info', 'get_related_objects_count')
    
    # Actions personnalisées
    actions = ['delete_users_safely']
    
    def get_chauffeur_info(self, obj):
        """Affiche les informations du chauffeur associé"""
        try:
            chauffeur = obj.chauffeur
            url = reverse('admin:drivers_chauffeur_change', args=[chauffeur.id])
            return format_html('<a href="{}">{} {}</a>', url, chauffeur.prenom, chauffeur.nom)
        except Chauffeur.DoesNotExist:
            return "Aucun chauffeur"
    get_chauffeur_info.short_description = 'Chauffeur associé'
    
    def get_superviseur_info(self, obj):
        """Affiche les informations de superviseur"""
        assignations = AssignationSuperviseur.objects.filter(superviseur=obj, actif=True)
        if assignations.exists():
            count = assignations.count()
            return format_html('<span style="color: green;">Superviseur ({} chauffeurs)</span>', count)
        return "Non superviseur"
    get_superviseur_info.short_description = 'Statut superviseur'
    
    def get_related_objects_count(self, obj):
        """Compte les objets liés à cet utilisateur"""
        chauffeur_count = Chauffeur.objects.filter(user=obj).count()
        assignations_count = AssignationSuperviseur.objects.filter(superviseur=obj).count()
        assignations_created_count = AssignationSuperviseur.objects.filter(assigne_par=obj).count()
        demandes_count = DemandeModification.objects.filter(admin_traite=obj).count()
        
        total = chauffeur_count + assignations_count + assignations_created_count + demandes_count
        
        if total > 0:
            return format_html('<span style="color: red; font-weight: bold;">{} objets liés</span>', total)
        return "Aucun objet lié"
    get_related_objects_count.short_description = 'Objets liés'
    
    def delete_users_safely(self, request, queryset):
        """
        Supprime les utilisateurs de manière sécurisée en gérant les dépendances
        
        Cette méthode :
        1. Vérifie les dépendances pour chaque utilisateur
        2. Supprime les objets liés en premier
        3. Supprime l'utilisateur en dernier
        4. Affiche un rapport détaillé
        """
        deleted_count = 0
        errors = []
        
        for user in queryset:
            try:
                with transaction.atomic():
                    # 1. Supprimer le chauffeur associé (si existe)
                    try:
                        chauffeur = user.chauffeur
                        chauffeur.delete()
                        self.message_user(request, f"Chauffeur '{chauffeur.nom_complet}' supprimé pour l'utilisateur '{user.username}'", messages.INFO)
                    except Chauffeur.DoesNotExist:
                        pass
                    
                    # 2. Supprimer les assignations où cet utilisateur est superviseur
                    assignations_as_supervisor = AssignationSuperviseur.objects.filter(superviseur=user)
                    assignations_count = assignations_as_supervisor.count()
                    if assignations_count > 0:
                        assignations_as_supervisor.delete()
                        self.message_user(request, f"{assignations_count} assignation(s) de superviseur supprimée(s) pour '{user.username}'", messages.INFO)
                    
                    # 3. Mettre à NULL les assignations créées par cet utilisateur
                    assignations_created = AssignationSuperviseur.objects.filter(assigne_par=user)
                    created_count = assignations_created.count()
                    if created_count > 0:
                        assignations_created.update(assigne_par=None)
                        self.message_user(request, f"{created_count} assignation(s) créée(s) mise(s) à NULL pour '{user.username}'", messages.INFO)
                    
                    # 4. Mettre à NULL les demandes de modification traitées par cet utilisateur
                    demandes_traitees = DemandeModification.objects.filter(admin_traite=user)
                    demandes_count = demandes_traitees.count()
                    if demandes_count > 0:
                        demandes_traitees.update(admin_traite=None)
                        self.message_user(request, f"{demandes_count} demande(s) de modification mise(s) à NULL pour '{user.username}'", messages.INFO)
                    
                    # 5. Supprimer l'utilisateur
                    username = user.username
                    user.delete()
                    deleted_count += 1
                    self.message_user(request, f"Utilisateur '{username}' supprimé avec succès", messages.SUCCESS)
                    
            except Exception as e:
                error_msg = f"Erreur lors de la suppression de '{user.username}': {str(e)}"
                errors.append(error_msg)
                self.message_user(request, error_msg, messages.ERROR)
        
        # Rapport final
        if deleted_count > 0:
            self.message_user(request, f"Suppression terminée : {deleted_count} utilisateur(s) supprimé(s) avec succès", messages.SUCCESS)
        
        if errors:
            self.message_user(request, f"{len(errors)} erreur(s) rencontrée(s)", messages.ERROR)
    
    delete_users_safely.short_description = "Supprimer les utilisateurs sélectionnés (sécurisé)"
    
    def get_queryset(self, request):
        """Optimise la requête en préchargeant les relations"""
        return super().get_queryset(request).select_related('chauffeur').prefetch_related(
            'assignationsuperviseur_set',
            'assignationsuperviseur_set__chauffeur',
            'demandemodification_set'
        )


# Désinscrire l'admin par défaut et inscrire notre admin personnalisé
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
