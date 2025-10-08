# =============================================================================
# COMMANDE DE GESTION - Suppression sécurisée des utilisateurs
# =============================================================================

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib import messages
from drivers.models import Chauffeur, AssignationSuperviseur
from activities.models import DemandeModification


class Command(BaseCommand):
    """
    Commande de gestion pour supprimer des utilisateurs de manière sécurisée
    
    Cette commande gère automatiquement toutes les dépendances avant de supprimer
    un utilisateur, évitant ainsi les erreurs de contrainte de clé étrangère.
    
    Usage :
    python manage.py delete_user_safely username1 username2 ...
    python manage.py delete_user_safely --all-inactive
    """
    
    help = 'Supprime des utilisateurs de manière sécurisée en gérant les dépendances'
    
    def add_arguments(self, parser):
        """Définit les arguments de la commande"""
        parser.add_argument(
            'usernames',
            nargs='*',
            help='Noms d\'utilisateur à supprimer'
        )
        parser.add_argument(
            '--all-inactive',
            action='store_true',
            help='Supprimer tous les utilisateurs inactifs'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait supprimé sans effectuer la suppression'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la suppression sans confirmation'
        )
    
    def handle(self, *args, **options):
        """Exécute la commande de suppression"""
        
        if options['all_inactive']:
            users_to_delete = User.objects.filter(is_active=False)
            self.stdout.write(f"Trouvé {users_to_delete.count()} utilisateur(s) inactif(s)")
        else:
            usernames = options['usernames']
            if not usernames:
                raise CommandError('Vous devez spécifier des noms d\'utilisateur ou utiliser --all-inactive')
            
            users_to_delete = User.objects.filter(username__in=usernames)
            not_found = set(usernames) - set(users_to_delete.values_list('username', flat=True))
            if not_found:
                raise CommandError(f'Utilisateur(s) non trouvé(s): {", ".join(not_found)}')
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('MODE DRY-RUN : Aucune suppression ne sera effectuée'))
            self.show_deletion_plan(users_to_delete)
            return
        
        if not options['force']:
            self.stdout.write(f"Vous êtes sur le point de supprimer {users_to_delete.count()} utilisateur(s):")
            for user in users_to_delete:
                self.stdout.write(f"  - {user.username} ({user.get_full_name() or 'Pas de nom'})")
            
            confirm = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ")
            if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(self.style.WARNING('Suppression annulée'))
                return
        
        # Effectuer la suppression
        deleted_count = 0
        errors = []
        
        for user in users_to_delete:
            try:
                with transaction.atomic():
                    self.delete_user_safely(user)
                    deleted_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Utilisateur "{user.username}" supprimé avec succès')
                    )
            except Exception as e:
                error_msg = f'✗ Erreur lors de la suppression de "{user.username}": {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
        
        # Rapport final
        self.stdout.write(f"\nRapport de suppression :")
        self.stdout.write(f"  - Utilisateurs supprimés : {deleted_count}")
        self.stdout.write(f"  - Erreurs : {len(errors)}")
        
        if errors:
            self.stdout.write(self.style.ERROR("\nDétails des erreurs :"))
            for error in errors:
                self.stdout.write(f"  {error}")
    
    def show_deletion_plan(self, users):
        """Affiche le plan de suppression sans l'exécuter"""
        self.stdout.write("\nPlan de suppression :")
        self.stdout.write("=" * 50)
        
        for user in users:
            self.stdout.write(f"\nUtilisateur : {user.username}")
            
            # Chauffeur associé
            try:
                chauffeur = user.chauffeur
                self.stdout.write(f"  → Chauffeur associé : {chauffeur.nom_complet} (sera supprimé)")
            except Chauffeur.DoesNotExist:
                self.stdout.write(f"  → Aucun chauffeur associé")
            
            # Assignations comme superviseur
            assignations_as_supervisor = AssignationSuperviseur.objects.filter(superviseur=user)
            count = assignations_as_supervisor.count()
            if count > 0:
                self.stdout.write(f"  → Assignations comme superviseur : {count} (seront supprimées)")
            
            # Assignations créées
            assignations_created = AssignationSuperviseur.objects.filter(assigne_par=user)
            count = assignations_created.count()
            if count > 0:
                self.stdout.write(f"  → Assignations créées : {count} (seront mises à NULL)")
            
            # Demandes de modification
            demandes = DemandeModification.objects.filter(admin_traite=user)
            count = demandes.count()
            if count > 0:
                self.stdout.write(f"  → Demandes de modification traitées : {count} (seront mises à NULL)")
    
    def delete_user_safely(self, user):
        """Supprime un utilisateur de manière sécurisée"""
        
        # 1. Supprimer le chauffeur associé (si existe)
        try:
            chauffeur = user.chauffeur
            chauffeur.delete()
            self.stdout.write(f"    → Chauffeur '{chauffeur.nom_complet}' supprimé")
        except Chauffeur.DoesNotExist:
            pass
        
        # 2. Supprimer les assignations où cet utilisateur est superviseur
        assignations_as_supervisor = AssignationSuperviseur.objects.filter(superviseur=user)
        count = assignations_as_supervisor.count()
        if count > 0:
            assignations_as_supervisor.delete()
            self.stdout.write(f"    → {count} assignation(s) de superviseur supprimée(s)")
        
        # 3. Mettre à NULL les assignations créées par cet utilisateur
        assignations_created = AssignationSuperviseur.objects.filter(assigne_par=user)
        count = assignations_created.count()
        if count > 0:
            assignations_created.update(assigne_par=None)
            self.stdout.write(f"    → {count} assignation(s) créée(s) mise(s) à NULL")
        
        # 4. Mettre à NULL les demandes de modification traitées par cet utilisateur
        demandes_traitees = DemandeModification.objects.filter(admin_traite=user)
        count = demandes_traitees.count()
        if count > 0:
            demandes_traitees.update(admin_traite=None)
            self.stdout.write(f"    → {count} demande(s) de modification mise(s) à NULL")
        
        # 5. Supprimer l'utilisateur
        user.delete()
