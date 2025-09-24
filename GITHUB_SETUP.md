# 🚀 Configuration GitHub pour Taxi App

## 📋 Étapes pour pousser le code sur GitHub

### 1. Créer un nouveau dépôt sur GitHub
1. Allez sur [GitHub.com](https://github.com)
2. Cliquez sur le bouton **"New"** ou **"+"** → **"New repository"**
3. Nom du dépôt : `taxi-app` ou `driver-app`
4. Description : `Application Django de suivi d'activité pour chauffeurs de taxi`
5. Choisissez **Public** ou **Private** selon vos préférences
6. **NE PAS** cocher "Add a README file" (nous en avons déjà un)
7. Cliquez sur **"Create repository"**

### 2. Connecter le dépôt local à GitHub
```bash
# Remplacez 'votre-username' par votre nom d'utilisateur GitHub
git remote add origin https://github.com/votre-username/taxi-app.git

# Pousser le code sur GitHub
git push -u origin main
```

### 3. Commandes alternatives selon votre configuration

#### Si vous utilisez SSH :
```bash
git remote add origin git@github.com:votre-username/taxi-app.git
git push -u origin main
```

#### Si vous avez déjà un dépôt existant :
```bash
git remote add origin https://github.com/votre-username/nom-du-depot.git
git branch -M main
git push -u origin main
```

## 🔧 Configuration Git (si nécessaire)

Si c'est votre premier push sur GitHub, configurez votre identité :
```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

## 📝 Informations du projet

- **Nom** : Taxi App
- **Description** : Application Django de suivi d'activité pour chauffeurs de taxi
- **Technologies** : Django 4.2.7, Bootstrap 5, SQLite/PostgreSQL
- **Langue** : Français
- **Licence** : À définir

## 🎯 Prochaines étapes après le push

1. **Activer GitHub Pages** (optionnel) pour héberger la documentation
2. **Configurer les Issues** pour le suivi des bugs et fonctionnalités
3. **Ajouter des badges** dans le README (build status, version, etc.)
4. **Configurer GitHub Actions** pour l'intégration continue
5. **Ajouter des collaborateurs** si nécessaire

## 📚 Documentation disponible

- `README.md` : Documentation complète du projet
- `DEMO.md` : Guide de démonstration
- `requirements.txt` : Dépendances Python
- `start.sh` : Script de démarrage automatique
