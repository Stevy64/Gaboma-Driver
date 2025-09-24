// Taxi App - JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
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

    // Auto-dismiss des alertes après 5 secondes
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirmation pour les actions importantes
    var confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Validation des formulaires
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Auto-format des numéros de téléphone
    var phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="telephone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var value = this.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.startsWith('0')) {
                    value = value.replace(/(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})/, '$1 $2 $3 $4 $5');
                } else if (value.startsWith('33')) {
                    value = value.replace(/(\d{2})(\d{1})(\d{2})(\d{2})(\d{2})(\d{2})/, '+$1 $2 $3 $4 $5 $6');
                }
            }
            this.value = value;
        });
    });

    // Auto-format des montants en euros
    var moneyInputs = document.querySelectorAll('input[name*="recette"], input[name*="montant"], input[name*="cout"]');
    moneyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(this.value);
            if (!isNaN(value) && value > 0) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Gestion des champs carburant (litres vs pourcentage)
    var carburantLitres = document.getElementById('carburant_litres');
    var carburantPourcentage = document.getElementById('carburant_pourcentage');
    
    if (carburantLitres && carburantPourcentage) {
        carburantLitres.addEventListener('input', function() {
            if (this.value) {
                carburantPourcentage.value = '';
                carburantPourcentage.disabled = true;
            } else {
                carburantPourcentage.disabled = false;
            }
        });

        carburantPourcentage.addEventListener('input', function() {
            if (this.value) {
                carburantLitres.value = '';
                carburantLitres.disabled = true;
            } else {
                carburantLitres.disabled = false;
            }
        });
    }

    // Animation de chargement pour les boutons de soumission
    var submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>En cours...';
                this.disabled = true;
                form.classList.add('loading');
            }
        });
    });

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

    // Gestion des modales de confirmation
    var confirmModal = document.getElementById('confirmModal');
    if (confirmModal) {
        var confirmButton = confirmModal.querySelector('#confirmButton');
        var confirmTitle = confirmModal.querySelector('#confirmTitle');
        var confirmMessage = confirmModal.querySelector('#confirmMessage');
        
        window.showConfirm = function(title, message, callback) {
            confirmTitle.textContent = title;
            confirmMessage.textContent = message;
            confirmButton.onclick = callback;
            var modal = new bootstrap.Modal(confirmModal);
            modal.show();
        };
    }

    // Validation en temps réel des signatures
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

    // Auto-save des formulaires (localStorage)
    var forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(function(form) {
        var formId = form.getAttribute('data-autosave');
        
        // Charger les données sauvegardées
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
        
        // Sauvegarder les données à chaque modification
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
        
        // Nettoyer après soumission
        form.addEventListener('submit', function() {
            localStorage.removeItem('form_' + formId);
        });
    });
});

// Fonctions utilitaires
function formatCurrency(amount) {
    return new Intl.NumberFormat('fr-FR', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(new Date(date));
}

function formatDateTime(date) {
    return new Intl.DateTimeFormat('fr-FR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Gestion des erreurs AJAX
function handleAjaxError(xhr, status, error) {
    console.error('Erreur AJAX:', error);
    var message = 'Une erreur est survenue. Veuillez réessayer.';
    
    if (xhr.responseJSON && xhr.responseJSON.message) {
        message = xhr.responseJSON.message;
    }
    
    showAlert('danger', message);
}

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
