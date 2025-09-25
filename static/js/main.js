// =============================================================================
// GABOMA DRIVE - JavaScript Principal
// =============================================================================
/**
 * Fichier JavaScript principal pour l'application Gaboma Drive
 * 
 * Ce fichier contient toutes les fonctionnalités JavaScript nécessaires
 * pour l'interface utilisateur de l'application de suivi d'activité de taxi.
 * 
 * Fonctionnalités principales :
 * - Gestion des alertes persistantes avec animation
 * - Validation des formulaires en temps réel
 * - Formatage automatique des données (téléphone, montants)
 * - Gestion des modales et confirmations
 * - Auto-save des formulaires
 * - Mise à jour de l'heure en temps réel
 * 
 * Compatibilité : ES5+ (pour support navigateurs anciens)
 * Dépendances : Bootstrap 5, jQuery (optionnel)
 */

// =============================================================================
// GESTION DES ALERTES PERSISTANTES - Système d'alertes avec auto-dismiss
// =============================================================================

/**
 * Initialise les alertes persistantes avec animation de disparition
 * 
 * Les alertes persistantes sont des messages qui restent affichés pendant
 * un temps défini (par défaut 60 secondes) puis disparaissent automatiquement
 * avec une animation de fondu. L'utilisateur peut aussi les fermer manuellement.
 * 
 * Fonctionnalités :
 * - Barre de progression visuelle
 * - Fermeture manuelle
 * - Pause sur survol de la souris
 * - Animation de disparition
 */
function initPersistentAlerts() {
    // Sélection de toutes les alertes avec la classe 'alert-persistent'
    var alerts = document.querySelectorAll('.alert-persistent');
    
    // Traitement de chaque alerte
    alerts.forEach(function(alert) {
        // Récupération du temps d'auto-dismiss (60 secondes par défaut)
        var autoDismissTime = parseInt(alert.getAttribute('data-auto-dismiss')) || 60000;
        
        // Éléments de l'alerte
        var progressBar = alert.querySelector('.alert-progress-bar');
        var closeButton = alert.querySelector('.btn-close');
        
        // Configuration de l'animation de la barre de progression
        if (progressBar) {
            progressBar.style.animationDuration = (autoDismissTime / 1000) + 's';
        }
        
        // Timer pour l'auto-dismiss
        var dismissTimer = setTimeout(function() {
            dismissAlert(alert);
        }, autoDismissTime);
        
        // Gestion de la fermeture manuelle
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                clearTimeout(dismissTimer);  // Annulation du timer
                dismissAlert(alert);
            });
        }
        
        // Pause de l'animation au survol de la souris
        alert.addEventListener('mouseenter', function() {
            if (progressBar) {
                progressBar.style.animationPlayState = 'paused';
            }
        });
        
        // Reprise de l'animation quand la souris quitte l'alerte
        alert.addEventListener('mouseleave', function() {
            if (progressBar) {
                progressBar.style.animationPlayState = 'running';
            }
        });
    });
}

/**
 * Ferme une alerte avec animation de fondu
 * 
 * @param {HTMLElement} alert - Élément alerte à fermer
 */
function dismissAlert(alert) {
    // Ajout de la classe CSS pour l'animation de disparition
    alert.classList.add('fade-out');
    
    // Suppression de l'élément après l'animation (500ms)
    setTimeout(function() {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 500); // Correspond à la durée de l'animation fadeOut définie en CSS
}

// =============================================================================
// INITIALISATION PRINCIPALE - Configuration au chargement de la page
// =============================================================================

/**
 * Initialisation principale de l'application
 * 
 * Cette fonction s'exécute quand le DOM est complètement chargé
 * et configure toutes les fonctionnalités JavaScript de l'interface.
 */
document.addEventListener('DOMContentLoaded', function() {
    // =============================================================================
    // INITIALISATION BOOTSTRAP - Composants UI
    // =============================================================================
    
    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialisation des popovers Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // =============================================================================
    // GESTION DES ALERTES - Système de notifications
    // =============================================================================
    
    // Initialisation des alertes persistantes
    initPersistentAlerts();

    // =============================================================================
    // GESTION DES CONFIRMATIONS - Actions critiques
    // =============================================================================
    
    // Confirmation pour les actions importantes (suppression, déconnexion, etc.)
    var confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();  // Annulation de l'action si l'utilisateur refuse
            }
        });
    });

    // =============================================================================
    // VALIDATION DES FORMULAIRES - Contrôles en temps réel
    // =============================================================================
    
    // Validation des formulaires avec feedback visuel
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');  // Activation du feedback visuel
        });
    });

    // =============================================================================
    // FORMATAGE AUTOMATIQUE - Amélioration de l'expérience utilisateur
    // =============================================================================
    
    // Auto-format des numéros de téléphone (format français et international)
    var phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="telephone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            // Suppression de tous les caractères non numériques
            var value = this.value.replace(/\D/g, '');
            if (value.length > 0) {
                // Format français : 01 23 45 67 89
                if (value.startsWith('0')) {
                    value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
                } 
                // Format international : +33 1 23 45 67 89
                else if (value.startsWith('33')) {
                    value = value.replace(/(\d{2})(\d{1})(\d{2})(\d{2})(\d{2})(\d{2})/, '+$1 $2 $3 $4 $5 $6');
                }
            }
            this.value = value;
        });
    });

    // Auto-format des montants en euros (2 décimales)
    var moneyInputs = document.querySelectorAll('input[name*="recette"], input[name*="montant"], input[name*="cout"]');
    moneyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(this.value);
            if (!isNaN(value) && value > 0) {
                this.value = value.toFixed(2);  // Formatage avec 2 décimales
            }
        });
    });

    // =============================================================================
    // GESTION DES CHAMPS SPÉCIAUX - Logique métier
    // =============================================================================
    
    // Gestion des champs carburant (mutuellement exclusifs : litres OU pourcentage)
    var carburantLitres = document.getElementById('carburant_litres');
    var carburantPourcentage = document.getElementById('carburant_pourcentage');
    
    if (carburantLitres && carburantPourcentage) {
        // Si l'utilisateur saisit des litres, désactiver le pourcentage
        carburantLitres.addEventListener('input', function() {
            if (this.value) {
                carburantPourcentage.value = '';
                carburantPourcentage.disabled = true;
            } else {
                carburantPourcentage.disabled = false;
            }
        });

        // Si l'utilisateur saisit un pourcentage, désactiver les litres
        carburantPourcentage.addEventListener('input', function() {
            if (this.value) {
                carburantLitres.value = '';
                carburantLitres.disabled = true;
            } else {
                carburantLitres.disabled = false;
            }
        });
    }

    // =============================================================================
    // FEEDBACK VISUEL - Amélioration de l'expérience utilisateur
    // =============================================================================
    
    // Animation de chargement pour les boutons de soumission
    var submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var form = this.closest('form');
            if (form && form.checkValidity()) {
                // Affichage du spinner et désactivation du bouton
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>En cours...';
                this.disabled = true;
                form.classList.add('loading');
            }
        });
    });

    // =============================================================================
    // MISE À JOUR TEMPORELLE - Affichage de l'heure en temps réel
    // =============================================================================
    
    // Mise à jour de l'heure en temps réel
    function updateTime() {
        var timeElements = document.querySelectorAll('.current-time');
        var now = new Date();
        var timeString = now.toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        timeElements.forEach(function(element) {
            element.textContent = timeString;
        });
    }
    
    // Mettre à jour l'heure toutes les minutes
    updateTime();
    setInterval(updateTime, 60000);

    // =============================================================================
    // GESTION DES MODALES - Interface de confirmation
    // =============================================================================
    
    // Gestion des modales de confirmation personnalisées
    var confirmModal = document.getElementById('confirmModal');
    if (confirmModal) {
        var confirmButton = confirmModal.querySelector('#confirmButton');
        var confirmTitle = confirmModal.querySelector('#confirmTitle');
        var confirmMessage = confirmModal.querySelector('#confirmMessage');
        
        // Fonction globale pour afficher une modale de confirmation
        window.showConfirm = function(title, message, callback) {
            confirmTitle.textContent = title;
            confirmMessage.textContent = message;
            confirmButton.onclick = callback;
            var modal = new bootstrap.Modal(confirmModal);
            modal.show();
        };
    }

    // =============================================================================
    // VALIDATION SPÉCIALISÉE - Contrôles métier spécifiques
    // =============================================================================
    
    // Validation en temps réel des signatures électroniques
    var signatureInputs = document.querySelectorAll('textarea[name="signature"]');
    signatureInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var value = this.value.trim();
            if (value.length < 3) {
                this.setCustomValidity('La signature doit contenir au moins 3 caractères');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // =============================================================================
    // AUTO-SAVE - Sauvegarde automatique des formulaires
    // =============================================================================
    
    // Auto-save des formulaires dans le localStorage
    var forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(function(form) {
        var formId = form.getAttribute('data-autosave');
        
        // Chargement des données sauvegardées au chargement de la page
        var savedData = localStorage.getItem('form_' + formId);
        if (savedData) {
            var data = JSON.parse(savedData);
            Object.keys(data).forEach(function(key) {
                var input = form.querySelector('[name="' + key + '"]');
                if (input && input.type !== 'password') {
                    input.value = data[key];
                }
            });
        }
        
        // Sauvegarde automatique à chaque modification
        form.addEventListener('input', function() {
            var formData = new FormData(form);
            var data = {};
            for (var pair of formData.entries()) {
                if (pair[1] && pair[0] !== 'csrfmiddlewaretoken') {
                    data[pair[0]] = pair[1];
                }
            }
            localStorage.setItem('form_' + formId, JSON.stringify(data));
        });
        
        // Nettoyage du localStorage après soumission réussie
        form.addEventListener('submit', function() {
            localStorage.removeItem('form_' + formId);
        });
    });
});

// =============================================================================
// FONCTIONS UTILITAIRES - Outils de formatage et d'affichage
// =============================================================================

/**
 * Formate un montant en devise française (euros)
 * 
 * @param {number} amount - Montant à formater
 * @returns {string} Montant formaté (ex: "1 234,56 €")
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

/**
 * Formate une date au format français
 * 
 * @param {string|Date} date - Date à formater
 * @returns {string} Date formatée (ex: "25/12/2023")
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(new Date(date));
}

/**
 * Formate une date et heure au format français
 * 
 * @param {string|Date} date - Date et heure à formater
 * @returns {string} Date et heure formatées (ex: "25/12/2023 14:30")
 */
function formatDateTime(date) {
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// =============================================================================
// GESTION DES ERREURS - Traitement des erreurs AJAX et affichage
// =============================================================================

/**
 * Gère les erreurs AJAX et affiche un message approprié
 * 
 * @param {XMLHttpRequest} xhr - Objet de requête XMLHttpRequest
 * @param {string} status - Statut de la requête
 * @param {string} error - Message d'erreur
 */
function handleAjaxError(xhr, status, error) {
    console.error('Erreur AJAX:', error);
    var message = 'Une erreur est survenue. Veuillez réessayer.';
    
    // Récupération du message d'erreur personnalisé si disponible
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    }
    
    showAlert('danger', message);
}

/**
 * Affiche une alerte Bootstrap dans l'interface
 * 
 * @param {string} type - Type d'alerte (success, warning, danger, info)
 * @param {string} message - Message à afficher
 */
function showAlert(type, message) {
    var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
        '</div>';
    
    var container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}
