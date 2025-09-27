# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drivers', '0003_assignationsuperviseur'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssignationSuperviseur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_assignation', models.DateTimeField(auto_now_add=True, verbose_name="Date d'assignation", help_text="Date et heure de l'assignation")),
                ('actif', models.BooleanField(default=True, verbose_name='Actif', help_text="Indique si l'assignation est active")),
                ('assigne_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignations_effectuees', to='auth.user', verbose_name='Assigné par', help_text="Utilisateur qui a effectué l'assignation")),
                ('chauffeur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='drivers.chauffeur', verbose_name='Chauffeur', help_text='Chauffeur assigné')),
                ('superviseur', models.ForeignKey(limit_choices_to={'groups__name': 'Superviseurs'}, on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='Superviseur', help_text='Superviseur assigné')),
            ],
            options={
                'verbose_name': 'Assignation Superviseur',
                'verbose_name_plural': 'Assignations Superviseurs',
                'ordering': ['-date_assignation'],
                'db_table': 'drivers_assignation_superviseur',
            },
        ),
        migrations.AddConstraint(
            model_name='assignationsuperviseur',
            constraint=models.UniqueConstraint(fields=('chauffeur', 'superviseur'), name='drivers_assignationsuperviseur_unique_chauffeur_superviseur'),
        ),
    ]
