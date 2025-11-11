#!/bin/bash
# =============================================================================
# SCRIPT DE DÉPLOIEMENT AUTOMATIQUE - Gaboma Driver App
# =============================================================================
# Ce script est appelé automatiquement par le webhook GitHub lors d'un push
# sur la branche principale (main/master).
#
# Actions effectuées :
# 1. Mise à jour du code depuis GitHub
# 2. Installation/mise à jour des dépendances Python
# 3. Application des migrations de base de données
# 4. Collecte des fichiers statiques
# 5. Rechargement de l'application Django
#
# Utilisation :
# - Automatique via webhook GitHub
# - Manuel : bash deploy.sh
# =============================================================================

set -e  # Arrêter le script en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Déterminer le répertoire du projet
# Sur PythonAnywhere, ajuster ce chemin selon votre configuration
PROJECT_DIR="/home/Gabomazone/Gaboma-Driver"
if [ ! -d "$PROJECT_DIR" ]; then
    # Si le chemin absolu n'existe pas, utiliser le répertoire courant
    PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

log_info "Démarrage du déploiement dans : $PROJECT_DIR"

# Aller dans le répertoire du projet
cd "$PROJECT_DIR" || {
    log_error "Impossible d'accéder au répertoire $PROJECT_DIR"
    exit 1
}

# Activer l'environnement virtuel si il existe
if [ -d "venv" ]; then
    log_info "Activation de l'environnement virtuel..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    log_info "Activation de l'environnement virtuel (répertoire parent)..."
    source ../venv/bin/activate
else
    log_warn "Aucun environnement virtuel trouvé, utilisation de Python système"
fi

# 1. Mise à jour du code depuis GitHub
log_info "Mise à jour du code depuis GitHub..."
git fetch origin || {
    log_error "Échec de la récupération depuis GitHub"
    exit 1
}

# Déterminer la branche principale (main ou master)
BRANCH="main"
if ! git show-ref --verify --quiet refs/heads/main; then
    BRANCH="master"
fi

log_info "Récupération de la branche $BRANCH..."
git pull origin "$BRANCH" || {
    log_error "Échec du pull depuis GitHub"
    exit 1
}

# 2. Installation/mise à jour des dépendances
if [ -f "requirements.txt" ]; then
    log_info "Installation/mise à jour des dépendances Python..."
    pip install -r requirements.txt --quiet --upgrade || {
        log_error "Échec de l'installation des dépendances"
        exit 1
    }
else
    log_warn "Fichier requirements.txt non trouvé, passage de l'étape d'installation"
fi

# 3. Application des migrations de base de données
log_info "Application des migrations de base de données..."
python manage.py migrate --noinput || {
    log_error "Échec de l'application des migrations"
    exit 1
}

# 4. Collecte des fichiers statiques
log_info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear || {
    log_warn "Échec de la collecte des fichiers statiques (peut être normal en développement)"
}

# 5. Rechargement de l'application Django
# Sur PythonAnywhere, toucher le fichier WSGI force le rechargement
WSGI_FILE="/var/www/gabomazone_pythonanywhere_com_wsgi.py"
if [ -f "$WSGI_FILE" ]; then
    log_info "Rechargement de l'application Django..."
    touch "$WSGI_FILE" || {
        log_warn "Impossible de toucher le fichier WSGI, rechargement manuel nécessaire"
    }
else
    log_warn "Fichier WSGI non trouvé à $WSGI_FILE, rechargement manuel nécessaire"
fi

log_info "Déploiement terminé avec succès !"
exit 0

