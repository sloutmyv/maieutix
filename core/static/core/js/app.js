/* Maieutix Application JavaScript */

// Global configuration
window.Maieutix = {
    config: {
        theme: {
            primary: '#2D4B73',
            secondary: '#253C59',
            accent: '#99B4BF',
            highlight: '#D9BA23',
            warning: '#BF8D30'
        }
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Maieutix application initialized');
    
    // Initialize HTMX custom configurations if needed
    if (window.htmx) {
        // HTMX event listeners avec debug amélioré
        document.body.addEventListener('htmx:beforeRequest', function(event) {
            console.log('HTMX request starting:', event.detail.requestConfig.path);
        });
        
        document.body.addEventListener('htmx:afterRequest', function(event) {
            console.log('HTMX request completed:', event.detail.xhr.status, event.detail.requestConfig.path);
            if (event.detail.xhr.status !== 200) {
                console.error('HTMX Error:', event.detail.xhr.responseText);
            }
        });
        
        document.body.addEventListener('htmx:responseError', function(event) {
            console.error('HTMX Response Error:', event.detail);
        });
        
        document.body.addEventListener('htmx:sendError', function(event) {
            console.error('HTMX Send Error:', event.detail);
        });

        // Gestion des événements personnalisés HTMX
        document.body.addEventListener('closeModal', function(event) {
            const modalContainer = document.getElementById('modal-container');
            if (modalContainer) {
                modalContainer.classList.add('hidden');
                modalContainer.innerHTML = '';
            }
        });

        // Gestion des clics sur les boutons de fermeture des modals
        document.body.addEventListener('click', function(event) {
            // Fermeture via boutons data-modal-close
            if (event.target.closest('[data-modal-close]')) {
                event.preventDefault();
                event.stopPropagation();
                console.log('Fermeture modal via bouton data-modal-close');
                const modalContainer = document.getElementById('modal-container');
                if (modalContainer) {
                    modalContainer.classList.add('hidden');
                    modalContainer.innerHTML = '';
                }
                return;
            }
            
            // Fermeture via clic sur l'overlay (background)
            if (event.target.id === 'modal-container') {
                console.log('Fermeture modal via clic overlay');
                const modalContainer = document.getElementById('modal-container');
                if (modalContainer) {
                    modalContainer.classList.add('hidden');
                    modalContainer.innerHTML = '';
                }
            }
        });

        // Gestion de l'affichage des modals quand le contenu est chargé
        document.body.addEventListener('htmx:afterSwap', function(event) {
            if (event.target.id === 'modal-container') {
                const modalContainer = document.getElementById('modal-container');
                if (modalContainer && modalContainer.innerHTML.trim()) {
                    modalContainer.classList.remove('hidden');
                    console.log('Modal affichée via HTMX afterSwap');
                    
                    // Ajouter un gestionnaire de clic sur l'overlay pour fermer la modal
                    modalContainer.onclick = function(e) {
                        if (e.target === modalContainer) {
                            window.closeModal();
                        }
                    };
                }
            }
        });

        // Gestion des touches clavier pour fermer les modals
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const modalContainer = document.getElementById('modal-container');
                if (modalContainer && !modalContainer.classList.contains('hidden')) {
                    console.log('Fermeture modal via touche Escape');
                    modalContainer.classList.add('hidden');
                    modalContainer.innerHTML = '';
                }
            }
        });

        document.body.addEventListener('refreshTable', function(event) {
            // Recharger le tableau des sages-femmes
            const tableContainer = document.getElementById('sagefemmes-table');
            if (tableContainer) {
                htmx.trigger(tableContainer, 'refresh');
            }
        });
    }
    
    // Initialize Alpine.js components
    if (window.Alpine) {
        console.log('Alpine.js is available');
    }
});

// Utility functions - keep only essential ones
window.Maieutix.utils = {};

// Fonction globale pour fermer les modals
window.closeModal = function() {
    console.log('closeModal appelée');
    const modalContainer = document.getElementById('modal-container');
    if (modalContainer) {
        modalContainer.classList.add('hidden');
        modalContainer.innerHTML = '';
    }
}