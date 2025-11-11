# =============================================================================
# WEBHOOK GITHUB - Déploiement automatique
# =============================================================================
"""
Endpoint webhook pour recevoir les notifications GitHub et déclencher
automatiquement le déploiement sur PythonAnywhere.

Sécurité :
- Vérification de la signature HMAC SHA256 pour authentifier les requêtes GitHub
- Utilisation d'une clé secrète partagée entre GitHub et l'application

Utilisation :
1. Configurer le webhook sur GitHub avec l'URL : https://votre-domaine.pythonanywhere.com/webhook/github/
2. Définir la clé secrète dans les variables d'environnement ou settings.py
3. Le webhook déclenche automatiquement le script deploy.sh lors d'un push
"""

import os
import subprocess
import hmac
import hashlib
import json
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings


def get_webhook_secret():
    """
    Récupère la clé secrète du webhook depuis les variables d'environnement
    ou depuis settings.py
    """
    return os.environ.get(
        'GITHUB_WEBHOOK_SECRET',
        getattr(settings, 'GITHUB_WEBHOOK_SECRET', '')
    )


def verify_github_signature(payload_body, signature_header):
    """
    Vérifie la signature HMAC SHA256 de la requête GitHub
    
    Args:
        payload_body: Corps de la requête (bytes)
        signature_header: En-tête X-Hub-Signature-256 de GitHub
    
    Returns:
        bool: True si la signature est valide, False sinon
    """
    if not signature_header:
        return False
    
    secret = get_webhook_secret()
    if not secret:
        # Si aucune clé secrète n'est configurée, on accepte toutes les requêtes
        # (non recommandé en production)
        return True
    
    # GitHub envoie la signature au format "sha256=..."
    if not signature_header.startswith('sha256='):
        return False
    
    # Extraire la signature
    received_signature = signature_header.split('sha256=')[1]
    
    # Calculer la signature attendue
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    # Comparaison sécurisée pour éviter les attaques par timing
    return hmac.compare_digest(received_signature, expected_signature)


@csrf_exempt
@require_POST
def github_webhook(request):
    """
    Endpoint pour recevoir les webhooks GitHub et déclencher le déploiement
    
    Méthode HTTP : POST uniquement
    Sécurité : Vérification de la signature GitHub (si configurée)
    
    Returns:
        HttpResponse: Réponse avec le résultat du déploiement
    """
    # Vérification de la signature GitHub
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
    payload_body = request.body
    
    if not verify_github_signature(payload_body, signature):
        return HttpResponseForbidden('Invalid signature')
    
    # Parser le payload JSON
    try:
        payload = json.loads(payload_body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponse(
            'Invalid JSON payload',
            status=400,
            content_type='text/plain'
        )
    
    # Vérifier que c'est bien un événement de type "push"
    event_type = request.META.get('HTTP_X_GITHUB_EVENT', '')
    if event_type != 'push':
        return HttpResponse(
            f'Event type "{event_type}" ignored. Only "push" events trigger deployment.',
            content_type='text/plain'
        )
    
    # Vérifier que c'est bien un push sur la branche principale (main ou master)
    ref = payload.get('ref', '')
    if ref not in ['refs/heads/main', 'refs/heads/master']:
        return HttpResponse(
            f'Push to branch "{ref}" ignored. Only pushes to main/master trigger deployment.',
            content_type='text/plain'
        )
    
    # Chemin du script de déploiement
    # Ajuster selon votre structure sur PythonAnywhere
    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'deploy.sh'
    )
    
    # Vérifier que le script existe
    if not os.path.exists(script_path):
        return HttpResponse(
            f'Deployment script not found at: {script_path}',
            status=500,
            content_type='text/plain'
        )
    
    # Exécuter le script de déploiement
    try:
        result = subprocess.run(
            ['bash', script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes maximum
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            response_text = f"""Deployment successful!

Branch: {ref}
Commit: {payload.get('head_commit', {}).get('id', 'N/A')[:7]}
Author: {payload.get('head_commit', {}).get('author', {}).get('name', 'N/A')}
Message: {payload.get('head_commit', {}).get('message', 'N/A')}

Output:
{result.stdout}
"""
            return HttpResponse(
                response_text,
                content_type='text/plain'
            )
        else:
            error_text = f"""Deployment failed!

Branch: {ref}
Commit: {payload.get('head_commit', {}).get('id', 'N/A')[:7]}

Error output:
{result.stderr}

Standard output:
{result.stdout}
"""
            return HttpResponse(
                error_text,
                status=500,
                content_type='text/plain'
            )
            
    except subprocess.TimeoutExpired:
        return HttpResponse(
            'Deployment script timed out after 5 minutes',
            status=500,
            content_type='text/plain'
        )
    except Exception as e:
        return HttpResponse(
            f'Error executing deployment script: {str(e)}',
            status=500,
            content_type='text/plain'
        )

