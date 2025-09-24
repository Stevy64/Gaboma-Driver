#!/bin/bash

# Script de démarrage pour Taxi App

echo "🚕 Démarrage de Taxi App..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si Django est installé
if ! python3 -c "import django" &> /dev/null; then
    echo "📦 Installation de Django..."
    pip3 install django
fi

# Appliquer les migrations
echo "🔄 Application des migrations..."
python3 manage.py migrate

# Créer un superutilisateur s'il n'existe pas
if ! python3 manage.py shell -c "from django.contrib.auth.models import User; print('Superuser exists:', User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
    echo "👤 Création du superutilisateur..."
    echo "admin" | python3 manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get_or_create(username='admin', defaults={'email': 'admin@taxi.com', 'is_staff': True, 'is_superuser': True})[0]; u.set_password('admin123'); u.save()"
fi

# Créer des données de test si demandé
read -p "🤔 Voulez-vous créer des données de test ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Création des données de test..."
    python3 create_test_data.py
fi

echo "🚀 Démarrage du serveur..."
echo "📍 Application disponible sur: http://localhost:8000"
echo "🔧 Administration Django: http://localhost:8000/admin"
echo ""
echo "👤 Comptes de test:"
echo "   Admin: admin / admin123"
echo "   Chauffeurs: jean.dupont / chauffeur123"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

python3 manage.py runserver 0.0.0.0:8000
