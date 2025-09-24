#!/bin/bash

# Script pour pousser Taxi App sur GitHub
echo "🚕 Pushing Taxi App to GitHub..."
echo "=" * 50

# Vérifier si Git est configuré
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git n'est pas configuré. Configuration nécessaire :"
    echo "git config --global user.name 'Votre Nom'"
    echo "git config --global user.email 'votre.email@example.com'"
    echo ""
    read -p "Voulez-vous continuer quand même ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Demander l'URL du dépôt GitHub
echo "📋 Configuration du dépôt GitHub"
echo "1. Créez un nouveau dépôt sur GitHub.com"
echo "2. Copiez l'URL du dépôt (ex: https://github.com/username/taxi-app.git)"
echo ""
read -p "URL du dépôt GitHub : " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ URL du dépôt requise"
    exit 1
fi

# Ajouter le remote origin
echo "🔗 Ajout du remote origin..."
git remote add origin "$repo_url" 2>/dev/null || git remote set-url origin "$repo_url"

# Pousser sur GitHub
echo "📤 Push vers GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Succès ! Votre code a été poussé sur GitHub"
    echo "🌐 Votre dépôt est disponible à : $repo_url"
    echo ""
    echo "📋 Prochaines étapes :"
    echo "1. Vérifiez votre dépôt sur GitHub"
    echo "2. Configurez les paramètres du dépôt si nécessaire"
    echo "3. Ajoutez des collaborateurs si besoin"
    echo "4. Configurez GitHub Actions pour l'intégration continue"
else
    echo "❌ Erreur lors du push. Vérifiez :"
    echo "- Votre connexion internet"
    echo "- Vos identifiants GitHub"
    echo "- L'URL du dépôt"
    echo "- Que le dépôt existe sur GitHub"
fi
