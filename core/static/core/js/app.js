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
                modalContainer.innerHTML = '';
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

// Utility functions
window.Maieutix.utils = {
    // Show notification
    notify: function(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        if (window.showNotification) {
            window.showNotification(message, type);
        }
    },
    
    // Confirm dialog
    confirm: function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    },
    
    // Format date
    formatDate: function(date) {
        return new Intl.DateTimeFormat('fr-FR').format(new Date(date));
    }
};