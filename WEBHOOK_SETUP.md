# Configuration du Webhook GitHub pour Déploiement Automatique

Ce guide explique comment configurer le webhook GitHub pour déployer automatiquement votre application Django sur PythonAnywhere.

## 📋 Fichiers créés

- `gabomadriver_app/webhook.py` : Endpoint Django pour recevoir les webhooks GitHub
- `deploy.sh` : Script bash pour automatiser le déploiement
- Configuration ajoutée dans `gabomadriver_app/urls.py` et `settings.py`

## 🚀 Étapes de configuration

### 1. Déployer les fichiers sur PythonAnywhere

1. Commitez et poussez les nouveaux fichiers sur GitHub :
   ```bash
   git add .
   git commit -m "Ajout du webhook GitHub pour déploiement automatique"
   git push origin main
   ```

2. Sur PythonAnywhere, récupérez les modifications :
   ```bash
   cd /home/Gabomazone/Gaboma-Driver
   git pull origin main
   ```

### 2. Rendre le script deploy.sh exécutable

Dans la console PythonAnywhere :
```bash
cd /home/Gabomazone/Gaboma-Driver
chmod +x deploy.sh
```

### 3. Ajuster les chemins dans deploy.sh (si nécessaire)

Ouvrez `deploy.sh` et vérifiez/modifiez ces variables selon votre configuration :

```bash
PROJECT_DIR="/home/Gabomazone/Gaboma-Driver"  # Chemin de votre projet
WSGI_FILE="/var/www/gabomazone_pythonanywhere_com_wsgi.py"  # Chemin de votre fichier WSGI
```

**Pour trouver votre fichier WSGI :**
- Allez dans le tableau de bord PythonAnywhere → Web
- Cliquez sur "WSGI configuration file"
- Le chemin complet s'affiche en haut du fichier

### 4. Générer une clé secrète pour le webhook

Dans la console PythonAnywhere, générez une clé secrète :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copiez la clé générée (ex: `a1b2c3d4e5f6...`)

### 5. Configurer la clé secrète sur PythonAnywhere

**Option A : Variable d'environnement (recommandé)**

Ajoutez dans votre fichier WSGI (avant `get_wsgi_application()`) :
```python
import os
os.environ['GITHUB_WEBHOOK_SECRET'] = 'votre-clé-secrète-ici'
```

**Option B : Dans settings.py (moins sécurisé)**

Modifiez `gabomadriver_app/settings.py` :
```python
GITHUB_WEBHOOK_SECRET = 'votre-clé-secrète-ici'
```

### 6. Ajouter le domaine PythonAnywhere dans ALLOWED_HOSTS

Dans `gabomadriver_app/settings.py`, ajoutez votre domaine :
```python
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    '0.0.0.0', 
    'testserver',
    'gabomazone.pythonanywhere.com',  # Votre domaine PythonAnywhere
]
```

### 7. Configurer le webhook sur GitHub

1. Allez sur votre repository GitHub → **Settings** → **Webhooks** → **Add webhook**

2. Remplissez le formulaire :
   - **Payload URL** : `https://gabomazone.pythonanywhere.com/webhook/github/`
     (Remplacez `gabomazone` par votre nom d'utilisateur PythonAnywhere)
   
   - **Content type** : `application/json`
   
   - **Secret** : Collez la clé secrète générée à l'étape 4
   
   - **Which events would you like to trigger this webhook?** : 
     Sélectionnez **"Just the push event"**
   
   - **Active** : ✅ Cochez la case

3. Cliquez sur **"Add webhook"**

### 8. Recharger l'application Django

Dans le tableau de bord PythonAnywhere → **Web** → Cliquez sur **"Reload [Your Site]"**

## 🧪 Tester le webhook

1. Faites un petit changement dans votre code (ex: ajoutez un commentaire)
2. Commitez et poussez :
   ```bash
   git add .
   git commit -m "Test du webhook"
   git push origin main
   ```
3. Vérifiez sur GitHub :
   - Allez dans **Settings** → **Webhooks** → Cliquez sur votre webhook
   - Regardez la section **"Recent Deliveries"**
   - Vous devriez voir une requête avec un code de réponse 200

4. Vérifiez sur PythonAnywhere :
   - Allez dans **Web** → **Error log** pour voir les logs
   - Vérifiez que votre code a bien été mis à jour

## 🔒 Sécurité

- ✅ La vérification de signature HMAC SHA256 est activée par défaut
- ✅ Seuls les événements "push" sur les branches main/master déclenchent le déploiement
- ✅ Le webhook nécessite une clé secrète pour fonctionner

## 🐛 Dépannage

### Le webhook ne se déclenche pas

1. Vérifiez que l'URL du webhook est correcte dans GitHub
2. Vérifiez que `ALLOWED_HOSTS` contient votre domaine PythonAnywhere
3. Consultez les logs d'erreur dans PythonAnywhere → Web → Error log

### Erreur "Invalid signature"

- Vérifiez que la clé secrète dans GitHub correspond à celle dans votre code
- Vérifiez que la variable d'environnement `GITHUB_WEBHOOK_SECRET` est bien définie

### Le script deploy.sh ne s'exécute pas

1. Vérifiez que le script est exécutable : `chmod +x deploy.sh`
2. Vérifiez les chemins dans `deploy.sh` (PROJECT_DIR, WSGI_FILE)
3. Testez le script manuellement : `bash deploy.sh`

### Erreur "ModuleNotFoundError"

- Vérifiez que tous les fichiers ont bien été poussés sur GitHub
- Vérifiez que `git pull` a bien récupéré les modifications sur PythonAnywhere

## 📝 Notes importantes

- Le webhook ne fonctionne que pour les pushes sur `main` ou `master`
- Le script `deploy.sh` a un timeout de 5 minutes maximum
- Les fichiers statiques sont collectés automatiquement
- L'application Django est rechargée automatiquement après le déploiement

## 🔄 Désactiver temporairement le webhook

Si vous devez désactiver le webhook temporairement :
1. Allez sur GitHub → Settings → Webhooks
2. Décochez la case **"Active"** sur votre webhook

Ou commentez l'URL dans `urls.py` :
```python
# path('webhook/github/', github_webhook, name='github_webhook'),
```

