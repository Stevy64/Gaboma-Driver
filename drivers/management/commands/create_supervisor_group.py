"""
Commande Django pour créer le groupe 'Superviseurs' et assigner les permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from activities.models import PriseCles, RemiseCles, Panne, DemandeModification
from drivers.models import Chauffeur


class Command(BaseCommand):
    help = 'Crée le groupe Superviseurs avec les permissions appropriées'

    def handle(self, *args, **options):
        # Créer le groupe Superviseurs
        group, created = Group.objects.get_or_create(name='Superviseurs')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Groupe "Superviseurs" créé avec succès')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Groupe "Superviseurs" existe déjà')
            )

        # Permissions pour les modèles
        models = [Chauffeur, PriseCles, RemiseCles, Panne, DemandeModification]
        
        for model in models:
            content_type = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=content_type)
            
            # Ajouter toutes les permissions (view, add, change, delete)
            for permission in permissions:
                group.permissions.add(permission)
                self.stdout.write(f'Permission ajoutée: {permission.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Groupe "Superviseurs" configuré avec {group.permissions.count()} permissions'
            )
        )

