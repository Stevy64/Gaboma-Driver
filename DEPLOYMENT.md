# 🚀 Guide de Déploiement - Gaboma Drive

## 📋 Prérequis

### Système
- **Python** : 3.8 ou supérieur
- **pip** : Gestionnaire de paquets Python
- **Git** : Contrôle de version
- **Base de données** : SQLite (développement) ou PostgreSQL (production)

### Comptes requis
- **GitHub** : Pour le dépôt de code
- **Serveur** : Pour le déploiement (optionnel)

## 🔧 Installation Locale

### 1. Cloner le dépôt
```bash
git clone https://github.com/votre-username/gaboma-drive.git
cd gaboma-drive
```

### 2. Environnement virtuel
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Linux/Mac :
source venv/bin/activate
# Windows :
venv\Scripts\activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données
```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

### 5. Démarrer le serveur
```bash
python manage.py runserver
```

## 🌐 Accès à l'application

### URLs principales
- **Accueil** : `http://localhost:8000/`
- **Connexion chauffeur** : `http://localhost:8000/login/`
- **Admin Django** : `http://localhost:8000/admin/`
- **Dashboard admin** : `http://localhost:8000/admin-dashboard/`

### Identifiants par défaut
- **Chauffeur test** :
  - Username : `chauffeur`
  - Password : `chauffeur123`

## 🎯 Fonctionnalités à tester

### 1. Connexion chauffeur
1. Aller à `http://localhost:8000/login/`
2. Utiliser les identifiants : `chauffeur` / `chauffeur123`
3. Vérifier la redirection vers le dashboard

### 2. Prise de clés (matin)
1. Se connecter en tant que chauffeur
2. Cliquer sur "Prendre les clés"
3. Remplir le formulaire :
   - Objectif de recette (ex: 50000 FCFA)
   - Plein de carburant : Oui/Non
   - Problème mécanique : Aucun
   - Signature : Texte simulé
4. Valider et vérifier le message de succès

### 3. Remise de clés (soir)
1. Après avoir pris les clés le matin
2. Cliquer sur "Remettre les clés"
3. Remplir le formulaire :
   - Recette réalisée (ex: 45000 FCFA)
   - Plein de carburant : Oui/Non
   - Problème mécanique : Aucun
   - Signature : Texte simulé
4. Valider et vérifier le message de performance

### 4. Dashboard admin
1. Aller à `http://localhost:8000/admin/`
2. Se connecter avec le superutilisateur
3. Naviguer dans les sections :
   - Chauffeurs
   - Prise de clés
   - Remise de clés
   - Recettes
   - Pannes

## 🐛 Dépannage

### Problème de connexion chauffeur
```bash
# Vérifier les chauffeurs
python manage.py shell
>>> from drivers.models import Chauffeur
>>> Chauffeur.objects.all()

# Réinitialiser le mot de passe
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='chauffeur')
>>> user.set_password('chauffeur123')
>>> user.save()
```

### Erreur de template
```bash
# Vérifier les templates
python manage.py check --deploy

# Collecter les fichiers statiques
python manage.py collectstatic
```

### Problème de base de données
```bash
# Réinitialiser les migrations
python manage.py migrate --fake-initial
python manage.py migrate
```

## 🚀 Déploiement en production

### 1. Configuration serveur
```bash
# Installer les dépendances système
sudo apt update
sudo apt install python3 python3-pip python3-venv postgresql nginx

# Cloner le projet
git clone https://github.com/votre-username/gaboma-drive.git
cd gaboma-drive
```

### 2. Configuration PostgreSQL
```sql
-- Créer la base de données
CREATE DATABASE gaboma_drive;
CREATE USER taxi_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE gaboma_drive TO taxi_user;
```

### 3. Configuration Django
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com', 'votre-ip']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'gaboma_drive',
        'USER': 'taxi_user',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Déploiement avec Gunicorn
```bash
# Installer Gunicorn
pip install gunicorn

# Démarrer l'application
gunicorn gaboma_drive.wsgi:application --bind 0.0.0.0:8000
```

### 5. Configuration Nginx
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /chemin/vers/gaboma-drive/staticfiles/;
    }
}
```

## 📊 Monitoring

### Logs
```bash
# Logs de l'application
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs Django
python manage.py runserver --verbosity=2
```

### Performance
```bash
# Vérifier les performances
python manage.py check --deploy
python manage.py collectstatic --noinput
```

## 🔒 Sécurité

### Checklist de sécurité
- [ ] `DEBUG = False` en production
- [ ] `SECRET_KEY` sécurisé
- [ ] `ALLOWED_HOSTS` configuré
- [ ] HTTPS activé
- [ ] Mots de passe forts
- [ ] Sauvegardes régulières

### Sauvegarde
```bash
# Sauvegarder la base de données
pg_dump gaboma_drive > backup_$(date +%Y%m%d).sql

# Sauvegarder les fichiers
tar -czf gaboma_drive_backup_$(date +%Y%m%d).tar.gz /chemin/vers/gaboma-drive/
```

## 📞 Support

### En cas de problème
1. **Vérifier les logs** : Consulter les logs d'erreur
2. **Tester localement** : Reproduire le problème en local
3. **Documenter** : Noter les étapes pour reproduire
4. **Contacter** : Ouvrir une issue sur GitHub

### Ressources utiles
- **Documentation Django** : https://docs.djangoproject.com/
- **Bootstrap** : https://getbootstrap.com/docs/
- **PostgreSQL** : https://www.postgresql.org/docs/

---

**🚕 Application Gaboma Drive - Prête pour la production !**
